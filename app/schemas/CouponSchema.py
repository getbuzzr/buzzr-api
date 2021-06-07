from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime


class CouponSchemaOut(BaseModel):
    id: int
    coupon_code: str
    credit: int
    valid_from: datetime
    valid_until: datetime
    date_redeemed: datetime


class CouponSchemaIn(BaseModel):
    coupon_code: str
