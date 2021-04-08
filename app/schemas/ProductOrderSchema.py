from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime


class ProductOrderSchemaOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    quantity: int
    order_id: int
    product_id: int
    id: int


class ProductOrderSchemaIn(BaseModel):
    """This schema is used to validate User api endpoint
    """
    quantity: int
    product_id: int
