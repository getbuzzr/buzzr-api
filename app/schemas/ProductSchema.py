from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime


class ProductSchemaOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    name: str
    category_id: int
    stock: int
    description: Optional[str]
    department_id: int
    weight: int
    cost: float
    tags: Optional[List[str]]
    pictures: Optional[List[str]]
    id: int
    percent_discount: int
