from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.Product import Product
from models.Department import Department
# schemas
from schemas.ProductSchema import ProductSchemaOut
# Auth
from auth import get_current_user
from utils import serialize
# utils
from database import get_db

router = APIRouter()


@router.get('/{category_id}/products', response_model=List[ProductSchemaOut])
def get_category_products(category_id: int,  session: Session = Depends(get_db)):
    return_product = session.query(Product).filter_by(
        category_id=category_id).all()
    return [x.serialize_product() for x in return_product]
