from pydantic import BaseModel, EmailStr, Field, ValidationError, validator
from typing import Optional


class PictureSchemaIn(BaseModel):
    """This file schema
    """
    name: str

    @validator('name')
    def name_must_be_pic(cls, v):
        if not v.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise ValueError('File must be image .png, .jpg, .jpeg')
        return v


class S3PresignedUrlSchemaOut(BaseModel):
    url: str
    key: str
    acl: str
    AWSAccessKeyId: str
    x_amz_security_token: str = Field(None, alias='x-amz-security-token')
    policy: str
    signature: str
