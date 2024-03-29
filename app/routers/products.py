from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
# Models
from models.Product import Product, product_tags
from models.User import User
# schemas
from schemas.ProductSchema import ProductSchemaOut, ProductTags, ProductStatusEnum
# Auth
from auth import get_current_user_sub, get_current_user
from utils import serialize
# utils
from database import session_scope

router = APIRouter()


@router.get('/{product_id}', response_model=ProductSchemaOut)
def get_product(product_id: int):
    with session_scope() as session:
        product = session.query(Product).get(product_id)
        if product is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND)
        return serialize(product)


@router.get('/{product_id}/tags', response_model=List[ProductTags])
def get_tags(product_id: int, current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        product = session.query(Product).get(product_id)
        if product is None:
            raise HTTPException(
                status.HTTP_400_CONFLICT, "Product doesnt exist")
        return [serialize(x) for x in product.tags]


@router.post('/{product_id}/favorite')
def add_favorites(product_id: int, current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        product = session.query(Product).get(product_id)
        if product is None:
            raise HTTPException(
                status.HTTP_400_CONFLICT, "Product doesnt exist")
        if product in current_user.favorite_products:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "This product already exists in favorites")
        current_user.favorite_products.append(product)
        session.add(current_user)
        session.commit()
        return status.HTTP_200_OK


@router.delete('/{product_id}/favorite')
def delete_favorites(product_id: int, current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        product = session.query(Product).get(product_id)
        if product is None:
            raise HTTPException(
                status.HTTP_400_CONFLICT, "Product doesnt exist")
        try:
            current_user.favorite_products.remove(product)
        except:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "This product is not favorited")
        session.commit()
        return status.HTTP_200_OK


@router.get('/{product_id}/related', response_model=List[ProductSchemaOut])
def get_related(product_id: int):
    with session_scope() as session:
        product = session.query(Product).get(product_id)
        if product is None:
            raise HTTPException(
                status.HTTP_400_CONFLICT, "Product doesnt exist")
        tag_ids = [x.id for x in product.tags]
        # get all products with same tags but not same product id
        related_items = session.query(Product).join(product_tags).filter(and_(
            product_tags.c.tag_id.in_(tag_ids), product_tags.c.product_id != product_id, Product.status == ProductStatusEnum.active)).all()[:10]
        return [serialize(x) for x in related_items]
