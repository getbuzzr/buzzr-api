from fastapi import APIRouter, HTTPException, Depends, status, Request, Form
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
import stripe
import os
import json
# Models
from models.Order import Order, OrderStatusEnum
from models.User import User
from models.Product import Product
from models.ProductOrdered import ProductOrdered

# Schemas
from schemas.OrderSchema import AdminOrderStatusSchemaEdit, OrderSchemaOut, OrderSchemaIn, OrderSchemaCreateOut, AdminOrderSchemaEdit
# Auth
from auth import get_current_user, is_admin
from utils import serialize, send_push_sns
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
    payment_intent = json.loads(payload)['data']['object']['payment_intent']
    order = session.query(Order).filter_by(
        stripe_payment_intent=payment_intent).first()
    if order is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "No payment found")
    datetime_now = datetime.datetime.utcnow
    order.status = OrderStatusEnum.paid
    user = session.query(User).get(order.user_id)
    if user.apn_token:
        send_push_sns(user.apn_token, "ios",
                      "Your Order has been successfully paid for. Our team will begin preparing your order shortly")
    if user.fcm_token:
        send_push_sns(user.fcm_token, "android",
                      "Your Order has been successfully paid for. Our team will begin preparing your order shortly")
    # set date order paid
    order.date_paid = datetime_now
    session.commit()
    # post order to slack webhook
    SlackWebhookClient().post_delivery(order.id, order.user.id, order.address,
                                       f"{current_user.first_name} {current_user.last_name}", order.products_ordered)
    return status.HTTP_200_OKe


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
    messages = {'preparing': "Your order is currently being prepared by our team",
                "out_for_delivery": "Your order is currently out for delivery. We will be there soon!",
                "delivered": "Your delivery driver has arrived!"}
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
    return status.HTTP_200_OK
