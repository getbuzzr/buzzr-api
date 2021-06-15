from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.User import User
from models.Product import Product
#  schemas
from schemas.ProductSchema import ProductSchemaOut
# Auth
from auth import get_current_user_sub, get_current_user
from utils import serialize
# utils
from database import session_scope

router = APIRouter()


@router.get('', response_model=List[ProductSchemaOut])
def get_favorites(current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
        # get all product tags
        current_user = get_current_user(current_user_sub, session)
        return [serialize(x) for x in current_user.favorite_products]
