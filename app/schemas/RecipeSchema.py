from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime
from schemas.RecipeItemSchema import RecipeItemSchemaOut


class RecipeSummarySchemaOut(BaseModel):
    id: int
    title: str
    description: str
    image_url: str
    total_time_seconds: int
    active_time_seconds: int
    date_created: datetime
    servings: int
    calories: int
    instructions: str


class RecipeSchemaOut(BaseModel):
    id: int
    title: str
    description: str
    image_url: str
    total_time_seconds: int
    active_time_seconds: int
    servings: int
    calories: int
    instructions: str
    date_created: datetime
    recipe_items: List[RecipeItemSchemaOut]
