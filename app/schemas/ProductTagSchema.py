from pydantic import BaseModel


class ProductTagSchemaIn(BaseModel):
    name: str
    tags: str
