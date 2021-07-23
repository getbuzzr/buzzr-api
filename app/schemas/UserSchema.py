from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from models.User import UserRoleEnum
from datetime import datetime


class UserSchemaIn(BaseModel):
    """This schema is used to validate User api endpoint
    """
    first_name: constr(min_length=1)
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
    first_name: Optional[constr(min_length=1)]
    last_name: Optional[constr(min_length=1)]
    phone_number: Optional[constr(min_length=8)]
    apn_token: Optional[str]
    fcm_token: Optional[str]
    profile_picture_url: Optional[str]
    role: Optional[UserRoleEnum]
    additional_information: Optional[str]


class UserPhoneNumberPut(BaseModel):
    phone_number: str
    phone_country_code: str


class UserSchemaOut(BaseModel):
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
    phone_verification_code: Optional[str]
    is_phone_verified: Optional[bool]
    credit: int
    phone_country_code: Optional[str]
    referral_code: str


class UserPaymentCardAddress(BaseModel):
    city: Optional[str]
    country: Optional[str]
    line1: Optional[str]
    line2: Optional[str]
    postal_code: Optional[str]
    state: Optional[str]


class UserPaymentBillingDetails(BaseModel):
    address: UserPaymentCardAddress
    email: Optional[str]
    name: Optional[str]
    phone: Optional[str]


class UserCardDetails(BaseModel):
    brand: str
    country: str
    exp_month: int
    exp_year: int
    last4: str


class UserPaymentMethods(BaseModel):
    id: str
    billing_details: UserPaymentBillingDetails
    card: UserCardDetails


class ReferralCodeIn(BaseModel):
    referral_code: str


class UserApnToken(BaseModel):
    apn_token: str
