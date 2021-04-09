from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.Order import Order, OrderStatusEnum
from models.User import User
from models.Product import Product
from models.ProductOrdered import ProductOrdered
from models.StripeApiClient import StripeApiClient

# Schemas
from schemas.OrderSchema import OrderSchemaOut, OrderSchemaIn, OrderSchemaCreateOut
# Auth
from auth import get_current_user
from utils import serialize
# utils
from database import get_db

router = APIRouter()


@router.get('', response_model=List[OrderSchemaOut])
def get_orders(current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    orders = session.query(Order).filter_by(
        user_id=current_user.id).order_by(Order.date_created.desc()).all()
    orders_to_return = []
    # serialize with products to order
    for order in orders:
        new_order = serialize(order)
        new_order['products_ordered'] = [
            serialize(x) for x in order.products_ordered]
        orders_to_return.append(new_order)
    return orders_to_return


@router.get('', response_model=List[OrderSchemaOut])
def get_orders(current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    orders = session.query(Order).filter_by(
        user_id=current_user.id).order_by(Order.date_created.desc()).all()
    orders_to_return = []
    # serialize with products to order
    for order in orders:
        new_order = serialize(order)
        new_order['products_ordered'] = [
            serialize(x) for x in order.products_ordered]
        orders_to_return.append(new_order)
    return orders_to_return


@router.post('', response_model=OrderSchemaCreateOut)
def post_orders(order: OrderSchemaIn, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    # check if user already has order
    if session.query(Order).filter_by(status=OrderStatusEnum.checking_out, user_id=current_user.id).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "User has active checkout")
    # calculate cost
    total_cost = 0.0
    # gather products ordered and remove stock
    products_ordered = session.query(Product).filter(
        Product.id.in_([x.product_id for x in order.products_ordered])).all()
    for product_ordered in products_ordered:
        quantity = [
            x.quantity for x in order.products_ordered if x.product_id == product_ordered.id][0]
        cost = product_ordered.cost
        # if there is a discount, calculate it
        if product_ordered.percent_discount != 0:
            cost = product_ordered.cost * \
                (100 - product_ordered.percent_discount) * 0.01
        total_cost += quantity * cost
        product_ordered.stock -= quantity

    # no cost calculated
    total_cost = round(total_cost, 2)
    if total_cost == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "No cost calculated, make sure cart not empty")
    payment_intent = StripeApiClient('cad').generate_payment_intent(
        current_user.stripe_id, total_cost)
    # create new order
    new_order = Order(user_id=current_user.id, cost=total_cost,
                      status=OrderStatusEnum.checking_out, stripe_payment_intent=payment_intent.id)
    session.add(new_order)
    session.commit()
    # create product orders
    products_ordered_create = []
    for ordered_product in order.products_ordered:
        products_ordered_create.append(ProductOrdered(
            order_id=new_order.id, product_id=ordered_product.product_id, quantity=ordered_product.quantity))
    session.bulk_save_objects(products_ordered_create)
    session.commit()
    return serialize(new_order)