from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.Department import Department
from models.User import User
from models.Category import Category
from models.Product import Product
# schemas
from schemas.DepartmentSchema import DepartmentSchemaOut
from schemas.CategorySchema import CategorySchemaOut
from schemas.ProductSchema import ProductSchemaOut
# Auth
from auth import get_current_user
from utils import serialize
# utils
from database import get_db

router = APIRouter()


@router.get('', response_model=List[DepartmentSchemaOut])
def get_departments(current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    return [serialize(x) for x in session.query(Department).all()]


@router.get('/{department_id}/categories', response_model=List[CategorySchemaOut])
def get_department_categories(department_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    return [serialize(x) for x in session.query(Category).filter_by(department_id=department_id).all()]


@router.get('/{department_id}/products', response_model=List[ProductSchemaOut])
def get_department_products(department_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    return_product = []
    # serialize pictures/tags as they are one to many
    for product in session.query(Product).filter_by(department_id=department_id).all():
        serialized_product = serialize(product)
        serialized_product['pictures'] = [
            serialize(x) for x in product.pictures]
        serialized_product['tags'] = [serialize(x) for x in product.tags]
        return_product.append(serialized_product)
    return return_product
