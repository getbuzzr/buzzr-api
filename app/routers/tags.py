from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.Department import Department
from models.User import User
from models.Product import Product, ProductStatusEnum
from models.ProductTag import ProductTag
# schemas
from schemas.ProductSchema import ProductSchemaOut
from schemas.ProductTagSchema import ProductTagOut
# Auth
from utils import serialize
# utils
from database import session_scope
from caching import redis_client, REDIS_TTL
import json
router = APIRouter()


@router.get('/featured', response_model=List[ProductTagOut])
def get_featured_tags():
    try:
        featured_tags = json.loads(
            redis_client.get("featured_tags").decode("utf-8"))
    except:
        with session_scope() as session:
            featured_tags = [serialize(x)
                             for x in session.query(ProductTag).filter_by(is_featured=True).all()]
            redis_client.set("featured_tags", json.dumps(
                featured_tags), REDIS_TTL)

    return featured_tags


@router.get('/{tag_id}/products', response_model=List[ProductSchemaOut])
def get_tag_items(department_id: int):
    # serialize pictures/tags as they are one to many

    with session_scope() as session:
        tag_products = session.query(Product).filter_by(
            department_id=department_id, status=ProductStatusEnum.active).all()
        return [serialize(x) for x in department_products]
