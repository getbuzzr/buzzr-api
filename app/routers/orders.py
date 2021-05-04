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
from models.SlackWebhookClient import SlackWebhookClient
from routers.addresses import calculate_address_delivery_fee

# Schemas
from schemas.OrderSchema import OrderSchemaOut, OrderSchemaIn, OrderSchemaCreateOut, OrderTipEditSchemaIn, OrderTipEditSchemaOut, OrderFeedbackSchemaIn
# Auth
from auth import get_current_user
from utils import serialize
# utils
from database import get_db

import json

router = APIRouter()


@router.delete('/{order_id}')
def delete_orders(order_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    order = session.query(Order).filter_by(
        user_id=current_user.id, id=order_id, status=OrderStatusEnum.checking_out).first()
    if order is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "active order doesnt exist or doesnt belong to user")
    # return stock to the product
    products_ordered = session.query(Product).filter(
        Product.id.in_([x.product_id for x in order.products_ordered])).all()
    for product_ordered in products_ordered:
        quantity = [
            x.quantity for x in order.products_ordered if x.product_id == product_ordered.id][0]
        product_ordered.stock += quantity
    session.delete(order)
    session.commit()
    return status.HTTP_200_OK


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


@router.get('/{order_id}', response_model=OrderSchemaOut)
def get_order_id(order_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    order = session.query(Order).filter_by(
        user_id=current_user.id, id=order_id).first()
    if order is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "order doesnt exist or you do not have access")
    new_order = serialize(order)
    new_order['products_ordered'] = [
        serialize(x) for x in order.products_ordered]
    return new_order


@router.put('/{order_id}/feedback')
def put_order_feedback(new_order_feedback: OrderFeedbackSchemaIn, order_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    order = session.query(Order).filter_by(
        user_id=current_user.id, id=order_id, status=OrderStatusEnum.complete).first()
    if order is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "order doesnt exist or you do not have acecess")
    order.feedback = new_order_feedback.feedback
    order.stars = new_order_feedback.stars
    session.commit()
    return status.HTTP_200_OK


@router.put('/{order_id}/tip_amount', response_model=OrderTipEditSchemaOut)
def put_order_tip(new_order_tip: OrderTipEditSchemaIn, order_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    order = session.query(Order).filter_by(
        user_id=current_user.id, id=order_id, status=OrderStatusEnum.checking_out).first()
    if order is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "order doesnt exist or you do not have access")
    old_tip = order.tip_amount
    cost_change = new_order_tip.tip_amount - old_tip
    new_cost = order.cost + cost_change
    # generate new payment intent secret
    payment_intent_secret = StripeApiClient('cad').edit_payment_intent(
        order.stripe_payment_intent, new_cost)
    order.cost = new_cost
    order.tip_amount = new_order_tip.tip_amount
    session.commit()
    return {"id": order.id, "cost": order.cost, "stripe_payment_intent_secret": payment_intent_secret}


@router.post('', response_model=OrderSchemaCreateOut)
def post_orders(order: OrderSchemaIn, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    # make sure order has one of address/lat/lng
    if order.address_id is None and order.latitude is None and (order.longitude is None or order.latitude is None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Must have address or lat long ")
    # check if user already has order
    if session.query(Order).filter_by(status=OrderStatusEnum.checking_out, user_id=current_user.id).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "User has active checkout")
    # calculate cost and tax amount
    total_cost = 0.0
    total_tax = 0.0
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
        # calculate tax amount
        tax_amount = cost * (product_ordered.tax/100)
        # calculate total cost of product with tax
        cost_with_tax = cost + tax_amount
        # append tax and total cost
        total_cost += quantity * cost_with_tax
        total_tax += tax_amount * quantity
        product_ordered.stock -= quantity
        if product_ordered.stock < 0:
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE,
                                detail=json.dumps({"reason": "out of stock", "product_id": product_ordered.id}))
    # add delivery fee,tip
    delivery_fee = calculate_address_delivery_fee(order.address_id)
    total_cost += delivery_fee
    total_cost += order.tip_amount
    # total cost calculated
    total_cost = round(total_cost, 2)
    # round tax for return
    total_tax = round(total_tax, 2)
    if total_cost == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "No cost calculated, make sure cart not empty")
    payment_intent = StripeApiClient('cad').generate_payment_intent(
        current_user.stripe_id, total_cost)
    # create new order
    new_order = Order(user_id=current_user.id, cost=total_cost, delivery_charge=delivery_fee, tax_charge=total_tax,
                      status=OrderStatusEnum.checking_out, stripe_payment_intent=payment_intent.id, tip_amount=order.tip_amount)
    # if order is associated with the address
    if order.address_id:
        new_order.address_id = order.address_id
    # if order is reliant on lat/lng
    else:
        new_order.latitude = order.latitude
        new_order.longitude = order.longitude
    session.add(new_order)
    session.commit()
    # create product orders
    products_ordered_create = []
    for ordered_product in order.products_ordered:
        products_ordered_create.append(ProductOrdered(
            order_id=new_order.id, product_id=ordered_product.product_id, quantity=ordered_product.quantity))
    session.bulk_save_objects(products_ordered_create)
    session.commit()
    return {"id": new_order.id, "cost":  new_order.cost, "tip_amount": order.tip_amount, "tax_charge": total_tax, "delivery_charge": delivery_fee, "stripe_payment_intent_secret": payment_intent.client_secret}
