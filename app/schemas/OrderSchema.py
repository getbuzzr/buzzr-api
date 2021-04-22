from pydantic import BaseModel, EmailStr, constr, conlist, validator
from typing import Optional, List
from datetime import datetime

from models.Order import StarRatingEnum, OrderStatusEnum
from schemas.ProductOrderSchema import ProductOrderSchemaOut, ProductOrderSchemaIn


class OrderSchemaIn(BaseModel):
    products_ordered: conlist(ProductOrderSchemaIn, min_items=1)
    address_id: Optional[int]
    longitude: Optional[float]
    latitude: Optional[float]


class OrderSchemaEdit(BaseModel):
    products_ordered: conlist(ProductOrderSchemaIn, min_items=1)


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
    date_created: datetime
    id: int
    stripe_payment_intent: str


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
