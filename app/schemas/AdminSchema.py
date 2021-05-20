

from pydantic import BaseModel, EmailStr, constr, conlist, validator
from typing import Optional, List
from datetime import datetime
from schemas.ProductOrderSchema import ProductOrderSchemaOut, ProductOrderSchemaIn

from models.Order import StarRatingEnum, OrderStatusEnum


class AdminOrderSchemaEdit(BaseModel):
    products_ordered: Optional[conlist(ProductOrderSchemaIn, min_items=1)]
    cost: Optional[int]
    status: Optional[OrderStatusEnum]


class AdminOrderStatusSchemaEdit(BaseModel):
    status: OrderStatusEnum


class StoreOpenSchema(BaseModel):
    is_store_open: bool


class NumRidersSchema(BaseModel):
    num_riders: int
