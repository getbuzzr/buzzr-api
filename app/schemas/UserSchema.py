from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from models.User import UserRoleEnum
from datetime import datetime


class UserSchemaIn(BaseModel):
    """This schema is used to validate User api endpoint
    """
    first_name: constr(min_length=2)
    last_name: constr(min_length=1)
    cognito_sub: str
    phone_number: Optional[constr(min_length=8)]
    email: EmailStr
    apn_token: Optional[str]
    fcm_token: Optional[str]
    profile_picture_url: Optional[str]


class UserSchemaPut(BaseModel):
    """This schema is used for validating fields allowed for put
    """
    first_name: Optional[constr(min_length=2)]
    last_name: Optional[constr(min_length=1)]
    phone_number: Optional[constr(min_length=8)]
    email: Optional[EmailStr]
    apn_token: Optional[str]
    fcm_token: Optional[str]
    profile_picture_url: Optional[str]
    role: Optional[UserRoleEnum]


class UserSchemaOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    first_name: str
    last_name: str
    cognito_sub: Optional[str]
    phone_number: Optional[str]
    email: EmailStr
    id: int
    profile_picture_url: Optional[str]
    role: UserRoleEnum
    additional_information: Optional[str]
    date_created: datetime
    apn_token: Optional[str]
    fcm_token: Optional[str]
    referral_id: Optional[str]
