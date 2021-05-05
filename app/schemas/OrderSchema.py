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
    tip_amount: float


class OrderSchemaEdit(BaseModel):
    products_ordered: conlist(ProductOrderSchemaIn, min_items=1)


class OrderTipEditSchemaIn(BaseModel):
    tip_amount: float


class OrderTipEditSchemaOut(BaseModel):
    stripe_payment_intent_secret:  str
    cost: float
    id: int


class AdminOrderSchemaEdit(BaseModel):
    products_ordered: Optional[conlist(ProductOrderSchemaIn, min_items=1)]
    cost: Optional[float]
    status: Optional[OrderStatusEnum]


class AdminOrderStatusSchemaEdit(BaseModel):
    status: OrderStatusEnum


class OrderSchemaCreateOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    cost: float
    id: int
    stripe_payment_intent_secret: str
    tax_charge: float
    delivery_charge: float
    tip_amount: float
    subtotal: float


class OrderSchemaOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    products_ordered: Optional[List[ProductOrderSchemaOut]]
    stars: Optional[StarRatingEnum]
    feedback: Optional[str]
    cost: float
    date_created: datetime
    date_delivered:  Optional[datetime]
    status: OrderStatusEnum
    id: int
    date_prepared:  Optional[datetime]
    date_out_for_delivery:  Optional[datetime]
    date_complete:  Optional[datetime]
    date_failed:  Optional[datetime]
    tip_amount:  Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[AddressSchemaOut]
    tax_charge: float
    delivery_charge: float
    subtotal: float


class OrderFeedbackSchemaIn(BaseModel):
    stars: StarRatingEnum
    feedback: constr(max_length=200)
