from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime
from schemas.ProductSchema import ProductSchemaOut
from models.RecipeItem import RecipeItemTypeEnum


class RecipeItemSchemaOut(BaseModel):
    id: int
    quantity: int
    product: ProductSchemaOut
    recipe_item_type: RecipeItemTypeEnum
