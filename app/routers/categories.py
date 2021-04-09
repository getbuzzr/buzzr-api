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
def get_department_products(department_id: int,  session: Session = Depends(get_db)):
    return_product = []
    # serialize pictures/tags as they are one to many
    for product in session.query(Product).filter_by(category_id=category_id).all():
        serialized_product = serialize(product)
        serialized_product['pictures'] = [
            serialize(x) for x in product.pictures]
        serialized_product['tags'] = [serialize(x) for x in product.tags]
        return_product.append(serialized_product)
    return return_product
