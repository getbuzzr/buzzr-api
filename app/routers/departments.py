from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.Department import Department
from models.User import User
from models.Category import Category
from models.Product import Product, ProductStatusEnum
# schemas
from schemas.DepartmentSchema import DepartmentSchemaOut
from schemas.CategorySchema import CategorySchemaOut
from schemas.ProductSchema import ProductSchemaOut
# Auth
from auth import get_current_user_sub
from utils import serialize
# utils
from database import session_scope
from caching import redis_client, REDIS_TTL
import json
router = APIRouter()


@router.get('', response_model=List[DepartmentSchemaOut])
def get_departments():
    try:
        departments = json.loads(
            redis_client.get("departments").decode("utf-8"))
    except:
        with session_scope() as session:
            departments = [serialize(x)
                           for x in session.query(Department).filter_by(is_active=True).order_by(Department.order.asc()).all()]
            redis_client.set("departments", json.dumps(
                departments), REDIS_TTL)

    return departments


@router.get('/{department_id}/categories', response_model=List[CategorySchemaOut])
def get_department_categories(department_id: int):
    try:
        categories = json.loads(
            redis_client.get(f"department_{department_id}_catagories").decode("utf-8"))
    except:
        with session_scope() as session:
            categories = [serialize(x)
                          for x in session.query(Category).filter_by(department_id=department_id, is_active=True).order_by(Category.order.asc()).all()]
            redis_client.set(
                "department_{department_id}_categories", json.dumps(categories), REDIS_TTL)
    return categories


@router.get('/{department_id}/products', response_model=List[ProductSchemaOut])
def get_department_products(department_id: int):
    # serialize pictures/tags as they are one to many
    with session_scope() as session:
        department_products = session.query(Product).filter_by(
            department_id=department_id, status=ProductStatusEnum.active).all()
        return [serialize(x) for x in department_products]
