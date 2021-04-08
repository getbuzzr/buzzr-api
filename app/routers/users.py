from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from schemas.UserSchema import UserSchemaOut, UserSchemaIn, UserSchemaPut
from schemas.FileSchema import PictureSchemaIn, S3PresignedUrlSchemaOut
# Models
from models.User import User, UserRoleEnum
from models.S3StaticFileClient import S3StaticFileClient

# Auth
from auth import get_current_user, has_user_read_update_perms, is_admin
from utils import serialize, validate_id_querystring
# utils
from database import get_db

router = APIRouter()


@router.get('', response_model=UserSchemaOut)
def retrieve_user_data(current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    return serialize(current_user)


@router.put('')
def edit_user(user_put_body: UserSchemaPut, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    # iterate through all the attributes of the usereditschema
    for key, value in user_put_body.dict().items():
        # If key is being edited
        if value:
            setattr(current_user, key, value)
    # push edits
    session.commit()
    return serialize(current_user)


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
