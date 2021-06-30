from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime
from schemas.RecipeItemSchema import RecipeItemSchemaOut


class RecipeSummarySchemaOut(BaseModel):
    id: int
    title: str
    description: str
    image_url: str
    cooking_time_seconds: int
    preperation_time_seconds: int
    date_created: datetime


class RecipeSchemaOut(BaseModel):
    id: int
    title: str
    description: str
    image_url: str
    cooking_time_seconds: int
    preperation_time_seconds: int
    date_created: datetime
    recipe_items: List[RecipeItemSchemaOut]
