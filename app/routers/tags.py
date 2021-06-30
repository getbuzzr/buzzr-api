from pytz import timezone, utc
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.Department import Department
from models.User import User
from models.Product import Product, ProductStatusEnum, product_tags
from models.ProductTag import ProductTag
from sqlalchemy import and_
# schemas
from schemas.ProductSchema import ProductSchemaOut
from schemas.ProductTagSchema import ProductTagSchemaOut
# Auth
from utils import serialize
# utils
from database import session_scope
from caching import redis_client, REDIS_TTL
import json
import random
router = APIRouter()


def get_pst_time():
    date_format = '%m_%d_%Y_%H_%M_%S_%Z'
    date = datetime.now(tz=utc)
    date = date.astimezone(timezone('US/Pacific'))
    return date


@router.get('/featured', response_model=List[ProductTagSchemaOut])
def get_featured_tags():
    pst_time = get_pst_time()
    try:
        featured_tags = json.loads(
            redis_client.get("featured_tags").decode("utf-8"))
    except:
        with session_scope() as session:
            # get time
            pst_time = get_pst_time()
            if pst_time.hour > 8 and pst_time.hour < 12:
                tags = session.query(ProductTag).filter(and_(ProductTag.is_featured == True, ProductTag.display_morning == True)
                                                        ).order_by(ProductTag.order.asc()).all()
            elif pst_time.hour >= 12 and pst_time.hour < 18:
                tags = session.query(ProductTag).filter(and_(ProductTag.is_featured == True, ProductTag.display_afternoon == True)
                                                        ).order_by(ProductTag.order.asc()).all()
            elif pst_time.hour >= 18 and pst_time.hour < 20:
                tags = session.query(ProductTag).filter(and_(ProductTag.is_featured == True, ProductTag.display_evening == True)
                                                        ).order_by(ProductTag.order.asc()).all()
            else:
                # else display night
                tags = session.query(ProductTag).filter(and_(ProductTag.is_featured == True, ProductTag.display_night == True)
                                                        ).order_by(ProductTag.order.asc()).all()
            featured_tags = [serialize(x)
                             for x in tags]
            redis_client.set("featured_tags", json.dumps(
                featured_tags), REDIS_TTL)

    return featured_tags


@router.get('/{tag_id}/products', response_model=List[ProductSchemaOut])
def get_tag_items(tag_id: int):
    # serialize pictures/tags as they are one to many
    with session_scope() as session:
        product_tag = session.query(ProductTag).get(tag_id)
        if product_tag is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        with session_scope() as session:
            tag_products = session.query(Product).join(product_tags).filter(and_(
                product_tags.c.tag_id == tag_id, Product.status == ProductStatusEnum.active)).all()[:10]
            products = [serialize(x) for x in tag_products]
            random.shuffle(products)
            return products
