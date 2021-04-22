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
from auth import get_current_user
from utils import serialize
# utils
from database import get_db

router = APIRouter()


@router.get('', response_model=List[ProductSchemaOut])
def get_favorites(current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    # get all product tags
    return [serialize(x) for x in current_user.favorite_products]
