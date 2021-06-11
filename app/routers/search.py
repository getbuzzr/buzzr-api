from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
# Models
from models.Product import Product, product_tags
from models.User import User
from models.Category import Category
from models.ProductTag import ProductTag
from models.PopularSearch import PopularSearch
from models.Search import Search
# schemas
from schemas.ProductSchema import ProductSchemaOut
from schemas.SearchSchema import SearchSchemaOut
# Auth
from auth import get_current_user
from utils import serialize
# utils
from database import get_db

router = APIRouter()


@router.get('', response_model=List[ProductSchemaOut])
def search(q: str = "", session: Session = Depends(get_db)):
    if len(q) < 2:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE,
                            "Your search must be  2 or more chars")
    # prepare search term
    search_term = f"%{q}%"
    # prepare products
    products = session.query(Product).filter(
        Product.name.like(search_term)).all()
    products_category = session.query(Category).filter(
        Category.name.like(search_term)).all()
    # get products that have tags in like search
    tags = session.query(ProductTag).filter(
        ProductTag.name.like(search_term)).all()
    tag_ids = [x.id for x in tags]
    products_with_tags = session.query(Product).join(product_tags).filter(
        product_tags.c.tag_id.in_(tag_ids)).all()
    searched_items = products + products_category + products_with_tags
    items_searched_unique = list(set(searched_items))
    search = Search(search_term=q)
    session.add(search)
    session.commit()
    return [serialize(x) for x in searched_items]


@router.get('/popular', response_model=List[SearchSchemaOut])
def search_popular(q: str = "", session: Session = Depends(get_db)):
    searches = session.query(PopularSearch).all()
    return [serialize(x) for x in searches]
