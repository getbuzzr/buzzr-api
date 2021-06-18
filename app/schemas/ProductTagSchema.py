from pydantic import BaseModel
from typing import Optional, List


class ProductTagSchemaIn(BaseModel):
    name: str
    tags: str


class ProductTagSchemaOut(BaseModel):
    name: str
    id: int
    order: Optional[int]
