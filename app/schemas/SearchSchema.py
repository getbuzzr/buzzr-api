from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime


class SearchSchemaOut(BaseModel):
    """This schema is used to validate User api endpoint
    """
    query: str
