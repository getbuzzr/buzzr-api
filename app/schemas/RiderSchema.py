from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime


class RiderSchemaOut(BaseModel):
    first_name: str
    last_name: str
    cognito_sub: Optional[str]
    phone_number: Optional[str]
    email: EmailStr
    id: int
    profile_picture_url: Optional[str]
    apn_token: Optional[str]
    fcm_token: Optional[str]
    phone_country_code: Optional[str]
