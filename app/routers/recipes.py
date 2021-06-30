from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
# Models
from models.Product import Product, product_tags
from models.User import User
from models.Recipe import Recipe
# schemas
from schemas.ProductSchema import ProductSchemaOut
from schemas.RecipeSchema import RecipeSchemaOut, RecipeSummarySchemaOut
# Auth
from auth import get_current_user_sub
from utils import serialize
# utils
from database import session_scope
from collections import OrderedDict
router = APIRouter()


@router.get('', response_model=List[RecipeSummarySchemaOut])
def get_all_recipes():
    with session_scope() as session:
        recipes = session.query(Recipe).all()
        return [serialize(x) for x in recipes]


@router.get('/{recipe_id}', response_model=RecipeSchemaOut)
def get_recipie(recipe_id: int):
    with session_scope() as session:
        recipe = session.query(Recipe).get(recipe_id)
        if recipe is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return_recipe = serialize(recipe)
        recipe_items = []
        for recipe_item in recipe.recipe_items:
            new_recipe_item = serialize(recipe_item)
            new_recipe_item['product'] = serialize(recipe_item.product)
            recipe_items.append(new_recipe_item)
        return_recipe['recipe_items'] = recipe_items
        return return_recipe
