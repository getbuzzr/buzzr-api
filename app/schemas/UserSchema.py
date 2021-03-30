from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from models.User import UserRoleEnum


class UserSchemaIn(BaseModel):
    """This schema is used to validate User api endpoint
    """
    first_name: constr(min_length=2)
    last_name: constr(min_length=1)
    cognito_sub: str
    phone_number: Optional[constr(min_length=8)]
    company: Optional[str]
    email: EmailStr
    organization_id: Optional[int]
    apn_token: Optional[str]
    fcm_token: Optional[str]
    profile_picture_url: Optional[str]


class UserSchemaPut(BaseModel):
    """This schema is used for validating fields allowed for put
    """
    first_name: Optional[constr(min_length=2)]
    last_name: Optional[constr(min_length=1)]
    company: Optional[str]
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
    company: Optional[str]
    email: EmailStr
    id: int
    organization_id: int
    profile_picture_url: Optional[str]
    role: UserRoleEnum
