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
from auth import get_current_user_sub
from utils import serialize
# utils
from database import session_scope
from collections import OrderedDict
router = APIRouter()


@router.get('', response_model=List[ProductSchemaOut])
def search(q: str = ""):
    search_term = f"%{q}%"
    initial_search = f"{q}%"
    space_search = f"% {q} %"
    with session_scope() as session:
        # prepare products
        products_space = session.query(Product).filter(
            Product.name.like(space_search)).all()
        products_initial = session.query(Product).filter(
            Product.search_term.like(initial_search)).all()
        products_initial_space = session.query(Product).filter(
            Product.search_term.like(search_term)).all()
        products_brand = session.query(Product).filter(
            Product.brand_name.like(initial_search)).all()
        products = session.query(Product).filter(
            Product.name.like(search_term)).all()
        category = session.query(Category).filter(
            Category.name.like(search_term)).all()
        products_category = session.query(Product).filter(
            Product.category_id.in_([x.id for x in category])).all()
        # get products that have tags in like search
        tags = session.query(ProductTag).filter(
            ProductTag.name.like(search_term)).all()
        tag_ids = [x.id for x in tags]
        products_with_tags = session.query(Product).join(product_tags).filter(
            product_tags.c.tag_id.in_(tag_ids)).all()
        searched_items = products_initial + products_initial_space + products_brand + products_space + products + \
            products_category + products_with_tags
        items_searched_unique = list(OrderedDict.fromkeys(searched_items))
        search = Search(search_term=q)
        session.add(search)
        session.commit()
        return [serialize(x) for x in items_searched_unique][:35]


@router.get('/popular', response_model=List[SearchSchemaOut])
def search_popular(q: str = ""):
    with session_scope() as session:
        searches = session.query(PopularSearch).all()
        return [serialize(x) for x in searches]
