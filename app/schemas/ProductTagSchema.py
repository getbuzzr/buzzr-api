from pydantic import BaseModel


class ProductTagSchemaIn(BaseModel):
    name: str
    tags: str

class ProductTagSchemaOut(BaseModel):
    name: str
    id: int
    
 