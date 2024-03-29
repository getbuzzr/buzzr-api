from pydantic import BaseModel, EmailStr, constr, conlist, validator
from typing import Optional, List
from datetime import datetime

from models.Order import StarRatingEnum, OrderStatusEnum
from schemas.ProductOrderSchema import ProductOrderSchemaOut, ProductOrderSchemaIn
from schemas.AddressSchema import AddressSchemaOut


class OrderSchemaIn(BaseModel):
    products_ordered: conlist(ProductOrderSchemaIn, min_items=1)
    address_id: Optional[int]
    longitude: Optional[float]
    latitude: Optional[float]
    tip_amount: int
    promo_code: Optional[str]


class OrderSchemaEdit(BaseModel):
    products_ordered: conlist(ProductOrderSchemaIn, min_items=1)


class OrderTipEditSchemaIn(BaseModel):
    tip_amount: int


class OrderSchemaCreateOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    cost: int
    id: int
    stripe_payment_intent_secret: Optional[str]
    tax_charge: int
    delivery_charge: int
    tip_amount: int
    subtotal: int
    stripe_ephemeral_key: Optional[str]
    stripe_customer_id: str
    credit_used: int
    promo_code_credit: Optional[int]
    applied_promo_code: Optional[str]


class OrderSchemaOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    products_ordered: Optional[List[ProductOrderSchemaOut]]
    stars: Optional[StarRatingEnum]
    feedback: Optional[str]
    cost: int
    date_created: datetime
    date_delivered:  Optional[datetime]
    status: OrderStatusEnum
    id: int
    date_preparing:  Optional[datetime]
    date_out_for_delivery:  Optional[datetime]
    date_complete:  Optional[datetime]
    date_arrived:  Optional[datetime]
    date_failed:  Optional[datetime]
    tip_amount:  Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[AddressSchemaOut]
    tax_charge: int
    delivery_charge: int
    subtotal: int
    credit_used: int
    promo_code_credit: Optional[int]
    applied_promo_code: Optional[str]


class OrderFeedbackSchemaIn(BaseModel):
    stars: StarRatingEnum
    feedback: constr(max_length=200)
