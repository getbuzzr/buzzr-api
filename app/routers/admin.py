from fastapi import APIRouter, HTTPException, Depends, status, Request, Form
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
import stripe
import os
import json
# Models
from models.Order import Order, OrderStatusEnum
from models.User import User, REFERRAL_USER_CREDIT
from models.Product import Product
from models.ProductOrdered import ProductOrdered
from models.SlackWebhookClient import SlackWebhookClient
import datetime
# Schemas
from schemas.OrderSchema import AdminOrderStatusSchemaEdit, OrderSchemaOut, OrderSchemaIn, OrderSchemaCreateOut, AdminOrderSchemaEdit
# Auth
from auth import get_current_user, is_admin
from utils import serialize, send_push_sns, generate_apple_order_push_payload
# utils
from database import get_db
router = APIRouter()


@router.get('/orders', response_model=List[OrderSchemaOut])
@is_admin
def get_orders(status: str = None, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    if status:
        orders = session.query(Order).filter_by(status=status).order_by(
            Order.date_created.desc()).all()
    else:
        orders = session.query(Order).order_by(
            Order.date_created.desc()).all()
    orders_to_return = []
    # serialize with products to order
    for order in orders:
        new_order = serialize(order)
        new_order['products_ordered'] = [
            serialize(x) for x in order.products_ordered]
        orders_to_return.append(new_order)
    return orders_to_return


@router.post('/orders/stripe_charge')
async def put_stripe_order(request: Request, session: Session = Depends(get_db)):
    endpoint_secret = os.environ['STRIPE_WEBHOOK_TOKEN']
    payload = await request.body()
    sig_header = request.headers['stripe-signature']
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HTTPException(status.HTTP_403_FORBIDDEN)
    payment_intent = json.loads(payload)['data']['object']['id']
    order = session.query(Order).filter_by(
        stripe_payment_intent=payment_intent).first()
    if order is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "No payment found")
    datetime_now = datetime.datetime.utcnow()
    order.status = OrderStatusEnum.paid
    user = session.query(User).get(order.user_id)
    if user.apn_token:
        send_push_sns(user.apn_token, "ios",
                      generate_apple_order_push_payload("Thank you for your order", f"Your order #{order.id} has been processed", OrderStatusEnum.paid))
    if user.fcm_token:
        send_push_sns(user.fcm_token, "android",
                      "Your Order has been successfully paid for. Our team will begin preparing your order shortly")
    # set date order paid
    order.date_paid = datetime_now
    # reward referring user for user purchase
    if user.referrer_id:
        # only reward if its first purchase
        if session.query(Order).filter_by(user_id=user.id).count() == 1:
            referrer = session.query(User).get(user.referrer_id)
            referrer.credit += REFERRAL_USER_CREDIT
    # subtract credit form user if credit was used
    if order.credit_used > 0:
        user.credit -= order.credit_used
    session.commit()
    # post order to slack webhook
    SlackWebhookClient().post_delivery(order.id, order.user.id, order.address,
                                       f"{order.user.first_name} {order.user.last_name}", order.products_ordered)
    return status.HTTP_200_OK


@router.put('/orders/{order_id}/status')
def create_user_notification(request: Request, order: AdminOrderStatusSchemaEdit, order_id: int, session: Session = Depends(get_db)):
    # allows retool to make post
    retool_auth_key = os.environ['RETOOL_AUTH_KEY']
    retool_key = request.headers['retool-auth-key']
    if retool_auth_key != retool_key:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You cant do this")
    edited_order = session.query(Order).get(order_id)
    if edited_order is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"order: {order_id} doesnt exist")
    # iterate through all the attributes of the usereditschema
    messages = {'preparing': generate_apple_order_push_payload("Your order is being prepared", f"Your order #{order_id} is now being prepared by our team", OrderStatusEnum.preparing),
                "out_for_delivery": generate_apple_order_push_payload("Your order is being delivered", f"Your order #{order_id} is now being delivered by a rider from our team. It will be there shortly", OrderStatusEnum.out_for_delivery),
                "delivered": generate_apple_order_push_payload("Your order has arrived", f"Your order #{order_id} has arrived!", OrderStatusEnum.out_for_delivery),
                "complete": generate_apple_order_push_payload("Thank you for your order", f"Your order #{order_id} has been completed!", OrderStatusEnum.complete)}
    try:
        message = messages[order.status.value]
    except:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "not supported update")
    targeted_user = session.query(User).get(edited_order.user_id)
    if targeted_user.apn_token:
        send_push_sns(targeted_user.apn_token, "ios", message)
    if targeted_user.fcm_token:
        send_push_sns(targeted_user.fcm_token, "android", message)
    # update the db
    datetime_now = datetime.datetime.utcnow()
    if order.status.value == "preparing":
        edited_order.date_preparing = datetime_now
    elif order.status.value == "out_for_delivery":
        edited_order.date_out_for_delivery = datetime_now
    elif order.status.value == "delivered":
        edited_order.date_delivered = datetime_now
    elif order.status.value == "complete":
        edited_order.date_complete = datetime_now
    session.commit()
    return status.HTTP_200_OK
