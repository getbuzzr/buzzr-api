from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.Product import Product
from models.User import User
# Auth
from auth import get_current_user
from utils import serialize
# utils
from database import get_db

router = APIRouter()


@router.post('/{product_id}/favorite')
def add_favorites(product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
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
def delete_favorites(product_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
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
