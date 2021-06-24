from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime


class CategorySchemaOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    name: str
    department_id: int
    order: Optional[int]
    id: int
