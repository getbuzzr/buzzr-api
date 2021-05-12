from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime
from models.Product import ProductUnitEnum, ProductStatusEnum


class ProductTags(BaseModel):
    id: int
    name: str


class ProductSchemaOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    name: str
    category_id: int
    stock: int
    description: Optional[str]
    department_id: int
    quantity: int
    cost: int
    image_url: Optional[str]
    id: int
    percent_discount: int
    tax: float
    unit: ProductUnitEnum
    status: ProductStatusEnum
