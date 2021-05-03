from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from schemas.UserSchema import UserSchemaOut, UserSchemaIn, UserSchemaPut, UserPhoneNumberPut
from schemas.FileSchema import PictureSchemaIn, S3PresignedUrlSchemaOut
# Models
from models.User import User, UserRoleEnum
from models.S3StaticFileClient import S3StaticFileClient

# Auth
from auth import get_current_user, has_user_read_update_perms, is_admin
from utils import serialize, validate_id_querystring
# utils
from database import get_db
from utils import validate_phone_number
import boto3
import random
router = APIRouter()


@router.get('', response_model=UserSchemaOut)
def retrieve_user_data(current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    return serialize(current_user)


@router.put('')
def edit_user(user_put_body: UserSchemaPut, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    # iterate through all the attributes of the usereditschema
    for key, value in user_put_body.dict().items():
        # If key is being edited
        if value is not None:
            setattr(current_user, key, value)
    # push edits
    session.commit()
    return serialize(current_user)


@router.put('/add_phone_number')
def add_user_phone(user_phone_number_put: UserPhoneNumberPut, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    phone_number = user_phone_number_put.phone_number
    if validate_phone_number(phone_number) == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Phone number not valid")
    verification_code = ''.join(random.sample('0123456789', 5))
    current_user.phone_number = phone_number
    current_user.phone_verification_code = verification_code
    client = boto3.client('sns')
    # send sms
    try:
        message = client.publish(PhoneNumber=phone_number,
                                 Message=f"Your buzzr verification code is {verification_code}")
    except Exception as e:
        logging.error(f'Exception sending sms')
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Couldnt send sms")
    session.commit()
    # send TODO sns to client to validat
    return status.HTTP_200_OK


@router.get('/confirm_phone_number')
def confirm_phone(verification_code: str = None, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    if verification_code is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Could not get verification_code in querystring")
    if verification_code != current_user.phone_verification_code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Wrong verificateion code")
    current_user.is_phone_verified = True
    session.commit()
    return status.HTTP_200_OK


@router.post("/upload_profile_picture", response_model=S3PresignedUrlSchemaOut)
def upload_profile_picture_post(file_upload: PictureSchemaIn, user_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    """Generate presigned s3 url for user to user to use to write to s3
    @returns sting: presigned s3 url

    """
    # initialize s3 client
    s3_client = S3StaticFileClient()
    # generate presigned url
    return_presigned_data = s3_client.generate_profile_picture_signed_url(
        current_user.id, file_upload.name)
    # switch profile picture
    profile_picture_url = f"{s3_client.STATIC_S3_BUCKET_NAME}/{return_presigned_data['key']}"
    current_user.profile_picture_url = profile_picture_url
    session.add(current_user)
    session.commit()
    # return presigned url
    return return_presigned_data
