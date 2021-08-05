from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from schemas.UserSchema import UserSchemaOut, UserSchemaIn, UserSchemaPut, UserPhoneNumberPut, UserPaymentMethods, ReferralCodeIn, UserApnToken
from schemas.FileSchema import PictureSchemaIn, S3PresignedUrlSchemaOut
# Models
from models.User import User, UserRoleEnum, REFERRAL_USER_CREDIT
from models.S3StaticFileClient import S3StaticFileClient
from models.CustomErrorMessage import UserErrorMessageEnum, CustomErrorMessage
# Auth
from auth import get_current_user_sub, has_user_read_update_perms, is_admin, get_current_user
from utils import serialize, validate_id_querystring
# utils
from database import session_scope
from utils import validate_phone_number
import boto3
import random
from models.StripeApiClient import StripeApiClient
from twilio.rest import Client
import os
router = APIRouter()


def subscribe_to_marketing_channel_sns(apn_token):
    """
    Generate application endpoint and subscribe to marketing channel
    Args:
        apn_token ([str]): This is the apn token of user

    Returns:
        [str]: The pllatform endpoint arn
    """
    client = boto3.client('sns')
    try:
        endpoint_response = client.create_platform_endpoint(
            PlatformApplicationArn=os.environ['IOS_SNS_PLATFORM_APPLICATION_ARN'],
            Token=apn_token,
        )['EndpointArn']
    except Exception as e:
        # case where user disabled endpoint response
        logging.error(e)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Couldnt create application ")
    marketing_sns_topic_arn = os.environ['MARKETING_TOPIC_ARN']
    try:
        response = client.subscribe(
            TopicArn=marketing_sns_topic_arn,
            Protocol='application',
            Endpoint=endpoint_response
        )
    except Exception as e:
        # case where user disabled endpoint response
        logging.error(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Couldnt subscribe user to topic")


@router.post("/referral_code")
def post_referral_code(referral_code: ReferralCodeIn, current_user_sub: User = Depends(get_current_user_sub)):
    """
    Apply referral code to user
    """
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        # user already referred
        if current_user.referrer_id is not None:
            raise HTTPException(status.HTTP_403_FORBIDDEN, CustomErrorMessage(
                UserErrorMessageEnum.ALREADY_REFFERED, error_message="User has already been referred").jsonify())
        # get referring user
        referring_user = session.query(User).filter_by(
            referral_code=referral_code.referral_code).first()
        # no user found
        if referring_user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        if referring_user.id == current_user.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, CustomErrorMessage(
                UserErrorMessageEnum.CANT_REFER_SELF, error_message="User cant refer self").jsonify())
        current_user.referrer_id = referring_user.id
        current_user.credit = REFERRAL_USER_CREDIT
        session.commit()
        return status.HTTP_200_OK


@router.post("/subscribe_marketing_sns")
def post_subscribe_sns(user_apn_token: UserApnToken):
    """
    subscribe apn to marketing topic
    """
    subscribe_to_marketing_channel_sns(user_apn_token.apn_token)
    return status.HTTP_200_OK


@router.get('', response_model=UserSchemaOut)
def retrieve_user_data(current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        return serialize(current_user)


@router.get('/get_payment_methods', response_model=List[UserPaymentMethods])
def get_payment_methods(current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        payment_methods = StripeApiClient(
            'cad').get_saved_payment_info(current_user.stripe_id)
        return payment_methods


@router.put('')
def edit_user(user_put_body: UserSchemaPut, current_user_sub: User = Depends(get_current_user_sub)):
    # iterate through all the attributes of the usereditschema
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        for key, value in user_put_body.dict().items():
            # If key is being edited
            if value is not None:
                setattr(current_user, key, value)
                # if new apn topic, create endpoint, subscribe to marketing topic
                if key == "apn_token":
                    subscribe_to_marketing_channel_sns(value)

        # push edits
        session.commit()
        return serialize(current_user)


@router.put('/add_phone_number')
def add_user_phone(user_phone_number_put: UserPhoneNumberPut, current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        phone_number = user_phone_number_put.phone_number
        country_code = user_phone_number_put.phone_country_code
        full_phone = f"+{country_code}{phone_number}"
        if validate_phone_number(full_phone) == False:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "Phone number not valid")
        verification_code = ''.join(random.sample('0123456789', 5))
        current_user.phone_number = phone_number
        current_user.phone_country_code = country_code
        current_user.phone_verification_code = verification_code
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)
        # send sms
        try:
            message = client.messages \
                .create(
                    body=f"Your Buzzr verification code is {verification_code}",
                    from_='+17786522895',
                    to=full_phone
                )
        except Exception as e:
            logging.error(f'Exception sending sms {e}')
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "Couldnt send sms")
        session.commit()
        return status.HTTP_200_OK


@router.get('/confirm_phone_number')
def confirm_phone(verification_code: str = None, current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        if verification_code is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "Could not get verification_code in querystring")
        if verification_code != current_user.phone_verification_code:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "Wrong verification code")
        current_user.is_phone_verified = True
        session.commit()
        return status.HTTP_200_OK


@router.post("/upload_profile_picture", response_model=S3PresignedUrlSchemaOut)
def upload_profile_picture_post(file_upload: PictureSchemaIn, user_id: int, current_user_sub: User = Depends(get_current_user_sub)):
    """Generate presigned s3 url for user to user to use to write to s3
    @returns sting: presigned s3 url

    """
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
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
