from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime


class DepartmentSchemaOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    picture_url: Optional[str]
    name: str
    id: int
