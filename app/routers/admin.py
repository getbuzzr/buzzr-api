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
from models.Department import Department
from models.Category import Category
from models.ProductOrdered import ProductOrdered
from models.SlackWebhookClient import SlackWebhookClient
from models.ProductTag import ProductTag
import datetime
# Schemas
from schemas.OrderSchema import OrderSchemaOut, OrderSchemaIn, OrderSchemaCreateOut
from schemas.AdminSchema import AdminOrderStatusSchemaEdit, AdminOrderSchemaEdit, StoreOpenSchema, NumRidersSchema
from schemas.ProductSchema import ProductSchemaIn, ProductTaxSchemaIn, ProductBrandIn, ProductSearchIn
from schemas.ProductTagSchema import ProductTagSchemaIn
# Auth
from auth import get_current_user_sub, is_admin
from utils import serialize, send_push_sns, generate_apple_order_push_payload
# utils
from database import session_scope
import boto3
router = APIRouter()


@router.get('/orders', response_model=List[OrderSchemaOut], include_in_schema=False)
@is_admin
def get_orders(status: str = None, current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
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


@router.post('/orders/stripe_charge', include_in_schema=False)
async def put_stripe_order(request: Request):
    with session_scope() as session:
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
                          generate_apple_order_push_payload("Thank you for your order", f"Your order #{order.id} has been processed.", OrderStatusEnum.paid))
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
        SlackWebhookClient().post_delivery(order.id, order.user,
                                           order.address, order.products_ordered)
        return status.HTTP_200_OK


@router.put('/orders/{order_id}/status', include_in_schema=False)
def create_user_notification(request: Request, order: AdminOrderStatusSchemaEdit, order_id: int):
    # allows retool to make post
    with session_scope() as session:
        retool_auth_key = os.environ['RETOOL_AUTH_KEY']
        retool_key = request.headers['retool-auth-key']
        if retool_auth_key != retool_key:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You cant do this")
        edited_order = session.query(Order).get(order_id)
        if edited_order is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                f"order: {order_id} doesnt exist")
        # if status update is complete, set in DB and dont sent user push
        datetime_now = datetime.datetime.utcnow()
        if order.status.value == "complete":
            edited_order.date_complete = datetime_now
            session.commit()
            return status.HTTP_200_OK
        # iterate through all the attributes of the usereditschema
        messages = {'preparing': generate_apple_order_push_payload("Your order is being prepared!", f"Your order #{order_id} is now being prepared by our team.", OrderStatusEnum.preparing),
                    "out_for_delivery": generate_apple_order_push_payload("Your order is being delivered!", f"Your order #{order_id} is now being delivered by a rider from our team. It will be there shortly.", OrderStatusEnum.out_for_delivery),
                    "arrived": generate_apple_order_push_payload("Your rider has arrived!", f"Your order #{order_id} has arrived!", OrderStatusEnum.arrived),
                    "delivered": generate_apple_order_push_payload("Your order has been delivered!", f"Your order #{order_id} has been completed! Thank you for using Buzzr and supporting local!", OrderStatusEnum.delivered),
                    }
        try:
            message = messages[order.status.value]
        except:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "not supported update")
        targeted_user = session.query(User).get(edited_order.user_id)

        # update the db
        if order.status.value == "preparing":
            edited_order.date_preparing = datetime_now
        elif order.status.value == "out_for_delivery":
            edited_order.date_out_for_delivery = datetime_now
        elif order.status.value == "arrived":
            edited_order.date_arrived = datetime_now
        elif order.status.value == "delivered":
            edited_order.date_delivered = datetime_now
        if targeted_user.apn_token:
            send_push_sns(targeted_user.apn_token, "ios", message)
        if targeted_user.fcm_token:
            send_push_sns(targeted_user.fcm_token, "android", message)
        session.commit()
        return status.HTTP_200_OK


@router.put('/change_rider_numbers', include_in_schema=False)
def change_rider_numbers(request: Request, riders: NumRidersSchema):
    with session_scope() as session:
        # allows retool to make post
        retool_auth_key = os.environ['RETOOL_AUTH_KEY']
        retool_key = request.headers['retool-auth-key']
        if retool_auth_key != retool_key:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You cant do this")
        client = boto3.client('ssm', region_name="us-east-1")
        try:
            parameter_value = client.put_parameter(
                Name='num_riders_working',
                Overwrite=True,
                Value=str(riders.num_riders))
            return parameter_value
        except Exception as e:
            logging.error(e)
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "Server has no ssm permission")
        return status.HTTP_200_OK


@router.put('/change_store_open', include_in_schema=False)
def change_store_open(request: Request, store_open: StoreOpenSchema):
    # allows retool to make post
    with session_scope() as session:
        retool_auth_key = os.environ['RETOOL_AUTH_KEY']
        retool_key = request.headers['retool-auth-key']
        if retool_auth_key != retool_key:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You cant do this")
        client = boto3.client('ssm', region_name="us-east-1")
        if store_open.is_store_open:
            store_open = "true"
        else:
            store_open = "false"
        try:
            parameter_value = client.put_parameter(
                Name='is_store_open',
                Overwrite=True,
                Value=store_open)
            return parameter_value
        except Exception as e:
            logging.error(e)
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "Server has no ssm permission")
        return status.HTTP_200_OK


@router.post('/products/create', include_in_schema=False)
def create_product(request: Request, product: ProductSchemaIn):
    # allows retool to make post
    with session_scope() as session:
        retool_auth_key = os.environ['RETOOL_AUTH_KEY']
        retool_key = request.headers['retool-auth-key']
        if retool_auth_key != retool_key:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You cant do this")
        department = session.query(Department).filter_by(
            name=product.department).first()
        # create department
        if department is None:
            new_department = Department(name=product.department)
            session.add(new_department)
            session.commit()
            department_id = new_department.id
        else:
            department_id = department.id

        category = session.query(Category).filter_by(
            name=product.category).first()
        if category is None:
            new_category = Category(name=product.category,
                                    department_id=department_id)
            session.add(new_category)
            session.commit()
            category_id = new_category.id
        else:
            category_id = category.id
        tax = 0
        if "p" in product.tax.lower():
            tax += 7
        if "g" in product.tax.lower():
            tax += 5
        product.cost.replace('.', '')
        existing_product = session.query(Product).filter(
            Product.image_url.contains(product.photo_id)).first()
        if existing_product:
            existing_product.name = product.name
            existing_product.quantity = product.quantity
            existing_product.description = product.description
            existing_product.category_id = category_id
            existing_product.department_id = department_id
            existing_product.brand_name = product.brand_name
            existing_product.tax = tax
            existing_product.cost = product.cost.replace('.', "")
            existing_product.image_url = f"https://static.getbuzzr.co/products/{product.photo_id}.jpg"
            existing_product.unit = product.unit.lower()
            existing_product.shelf_number = product.shelf_number
            existing_product.search_term = product.search_term
            product_targeted = existing_product
        else:
            new_product = Product(name=product.name,
                                  quantity=product.quantity,
                                  description=product.description,
                                  category_id=category_id,
                                  department_id=department_id,
                                  stock=product.stock,
                                  brand_name=product.brand_name,
                                  tax=tax,
                                  cost=product.cost.replace('.', ""),
                                  image_url=f"https://static.getbuzzr.co/products/{product.photo_id}.jpg",
                                  unit=product.unit.lower(),
                                  search_term=product.search_term,
                                  shelf_number=product.shelf_number)
            session.add(new_product)
            product_targeted = new_product
        session.commit()
        for tag in product.tags:
            tag_targeted = session.query(
                ProductTag).filter_by(name=tag).first()
            if tag_targeted is None:
                new_tag = ProductTag(name=tag)
                session.add(new_tag)
                session.commit()
                tag_targeted = new_tag

            if tag_targeted in product_targeted.tags:
                continue

            product_targeted.tags.append(tag_targeted)
            session.commit()
        return status.HTTP_200_OK
