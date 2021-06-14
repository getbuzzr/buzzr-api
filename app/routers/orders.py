from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
# Models
from models.Order import Order, OrderStatusEnum
from models.User import User
from models.Product import Product
from models.ProductOrdered import ProductOrdered
from models.StripeApiClient import StripeApiClient
from models.SlackWebhookClient import SlackWebhookClient
from models.CustomErrorMessage import OrderErrorMessageEnum, CustomErrorMessage, PromoCodeErrorMessage
from models.PromoCode import PromoCode
from models.Address import Address
from utils import get_parameter_from_ssm
# routers
from routers.addresses import calculate_address_delivery_fee
# Schemas
from schemas.OrderSchema import OrderSchemaOut, OrderSchemaIn, OrderSchemaCreateOut, OrderTipEditSchemaIn,  OrderFeedbackSchemaIn
# Auth
from auth import get_current_user
from utils import serialize, send_push_sns, generate_apple_order_push_payload
# utils
from database import get_db
import datetime
import json

MIN_ORDER_THRESHOLD = 50

router = APIRouter()


def re_add_stock(order, session):
    """Re adds all the stock that the order currently uses

    Args:
        order ([Order]): The order we want to readd
        session [DBSession] the db session

    """
    products_in_order = order.products_ordered
    for product_ordered in products_in_order:
        product_ordered.product.stock += product_ordered.quantity
    session.commit()


def check_promo_code(order, session):
    """Check to see if order has pormo code associated. If it does, remove from Promocode model and increase num_redeemed allowed

    Args:
        order ([type]): [description]
        session ([type]): [description]
    """
    if order.promo_code_id:
        old_promo_code = session.query(PromoCode).get(
            order.promo_code_id)
        if old_promo_code:
            old_promo_code.num_redeems_allowed += 1
            old_promo_code.orders.remove(order)
            session.commit()


@router.delete('')
def delete_orders(current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    order = session.query(Order).filter_by(
        user_id=current_user.id, status=OrderStatusEnum.checking_out).first()
    if order is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "actve order doesnt exist or doesnt belong to user")
    # check_promo_code(order, session)
    re_add_stock(order, session)
    # return stock to the product
    session.delete(order)
    session.commit()
    return status.HTTP_200_OK


@router.get('', response_model=List[OrderSchemaOut])
def get_orders(current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    orders = session.query(Order).filter_by(
        user_id=current_user.id).filter(Order.status != OrderStatusEnum.checking_out).order_by(Order.date_created.desc()).all()
    orders_to_return = []
    # serialize with products to order
    for order in orders:
        new_order = serialize(order)
        new_order['products_ordered'] = [
            serialize(x) for x in order.products_ordered]
        if order.address:
            new_order['address'] = serialize(order.address)
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
    if order.address:
        new_order['address'] = serialize(order.address)
    return new_order


@router.put('/{order_id}/feedback')
def put_order_feedback(new_order_feedback: OrderFeedbackSchemaIn, order_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    order = session.query(Order).filter(
        and_(Order.user_id == current_user.id, Order.id == order_id)).filter(Order.status.in_([OrderStatusEnum.failed, OrderStatusEnum.complete])).first()
    if order is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            CustomErrorMessage(
                                OrderErrorMessageEnum.NO_FEEDBACK_ALLOWED, error_message="Cant leave feedback for offer", error_detail="This is not the user's order or order doesnt have failed/complete status").jsonify())
    order.feedback = new_order_feedback.feedback
    order.stars = new_order_feedback.stars
    session.commit()
    return status.HTTP_200_OK


# @router.put('/{order_id}/tip_amount', response_model=OrderTipEditSchemaOut)
# def put_order_tip(new_order_tip: OrderTipEditSchemaIn, order_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
#     order = session.query(Order).filter_by(
#         user_id=current_user.id, id=order_id, status=OrderStatusEnum.checking_out).first()
#     if order is None:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST,
#                             "order doesnt exist or you do not have access")
#     old_tip = order.tip_amount
#     cost_change = new_order_tip.tip_amount - old_tip
#     new_cost = order.cost + cost_change
#     # generate new payment intent secret
#     payment_intent_secret = StripeApiClient('cad').edit_payment_intent(
#         order.stripe_payment_intent, new_cost)
#     stripe_ephemeral_key = StripeApiClient('cad').generate_ephemeral_key(
#         current_user.stripe_id)
#     order.cost = new_cost
#     order.tip_amount = new_order_tip.tip_amount
#     session.commit()
#     return {"id": order.id, "cost": order.cost, "stripe_payment_intent_secret": payment_intent_secret, 'stripe_customer_id': current_user.stripe_id, 'stripe_ephemeral_key': stripe_ephemeral_key.secret}


@router.post('', response_model=OrderSchemaCreateOut)
def post_orders(order: OrderSchemaIn, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    if current_user.is_phone_verified is False:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            CustomErrorMessage(
                                OrderErrorMessageEnum.PHONE_NOT_VERIFIED, error_message="User phone number not verified", error_detail="User's phone must be verified before they place an order").jsonify())
    # make sure order has one of address/lat/lng
    if order.address_id is None and order.latitude is None and (order.longitude is None or order.latitude is None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            CustomErrorMessage(
                                OrderErrorMessageEnum.ADDRESS_LAT_LNG_NOT_PRESENT, error_message="Order must have address of lat/lng").jsonify())
    # check to see if store is open
    if get_parameter_from_ssm('is_store_open') == "false":
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE,
                            CustomErrorMessage(
                                OrderErrorMessageEnum.STORE_NOT_OPEN, error_message="Store is not open").jsonify())
    # check to see if we have enough bikers to fulfill the orders
    current_order_count = session.query(Order).filter(
        Order.status.in_([OrderStatusEnum.preparing, OrderStatusEnum.paid, OrderStatusEnum.out_for_delivery, OrderStatusEnum.delivered])).count()
    if current_order_count >= int(get_parameter_from_ssm('num_riders_working')):
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE,
                            CustomErrorMessage(
                                OrderErrorMessageEnum.MAX_ORDERS_REACHED, error_message="We are currently too busy").jsonify())
    # check if user already has order in "checking out"
    preexisting_order = session.query(Order).filter_by(
        status=OrderStatusEnum.checking_out, user_id=current_user.id).first()
    if preexisting_order:
        # if preexisting order has a promo code, remove from Promocode model and add num_redeem_allowed
        # check_promo_code()
        # if preexisting_order.promo_code_id:
        #     old_promo_code = session.query(PromoCode).get(
        #         preexisting_order.promo_code_id)
        #     if old_promo_code:
        #         old_promo_code.num_redeems_allowed += 1
        #         old_promo_code.orders.remove(preexisting_order)
        #         session.commit()
        re_add_stock(preexisting_order, session)
        session.delete(preexisting_order)
    # if address is specified, check if it exists
    if order.address_id:
        address_delievered_to = session.query(Address).get(order.address_id)
        if address_delievered_to is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                CustomErrorMessage(
                                    OrderErrorMessageEnum.ADDRESS_DOESNT_EXIST, error_message="Address doesnt exist").jsonify())
        if address_delievered_to.is_serviceable == False:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                CustomErrorMessage(
                                    OrderErrorMessageEnum.ADDRESS_NOT_SERVICEABLE, error_message="Must deliver to serviceable address").jsonify())

    # If promo code is specified, check if it exists and check if user has already used it
    # promo_code_credit = None
    # if order.promo_code:
    #     current_datetime = datetime.datetime.utcnow()
    #     promo_code_targeted = session.query(PromoCode).filter(and_(
    #         PromoCode.promo_code == order.promo_code, PromoCode.valid_from < current_datetime, current_datetime < PromoCode.valid_until), PromoCode.num_redeems_allowed > 0).first()

    #     if promo_code_targeted is None:
    #         raise HTTPException(status.HTTP_400_BAD_REQUEST,
    #                             CustomErrorMessage(
    #                                 PromoCodeErrorMessage.NOT_VALID, error_message="This promocode is not valid or has expired").jsonify())
    #     # check to see if user has already used the promo code
    #     offer_with_promocode_applied = session.query(Order).filter_by(
    #         user_id=current_user.id, promo_code_id=promo_code_targeted.id).first()
    #     if offer_with_promocode_applied:
    #         raise HTTPException(status.HTTP_400_BAD_REQUEST,
    #                             CustomErrorMessage(
    #                                 PromoCodeErrorMessage.ALREADY_REDEEMED, error_message="This promo code has already been redeemed by this user").jsonify())
    #     promo_code_credit = promo_code_targeted.credit
    # check to see if the address exists
    # calculate cost and tax amount
    total_cost = 0
    total_tax = 0
    subtotal = 0
    # gather products ordered and remove stock
    products_ordered = session.query(Product).filter(
        Product.id.in_([x.product_id for x in order.products_ordered])).all()
    for product_ordered in products_ordered:
        quantity = [
            x.quantity for x in order.products_ordered if x.product_id == product_ordered.id][0]
        cost = product_ordered.cost
        # if there is a discount, calculate it
        if product_ordered.percent_discount != 0:
            cost = int(round(product_ordered.cost *
                             (100 - product_ordered.percent_discount) * 0.01))
        # calculate tax amount
        tax_amount = int(round(cost * (product_ordered.tax/100)))
        # calculate total cost of product with tax
        cost_with_tax = cost + tax_amount
        # append tax and total cost, subtotal
        subtotal += quantity * cost
        total_cost += quantity * cost_with_tax
        total_tax += tax_amount * quantity
        product_ordered.stock -= quantity
        if product_ordered.stock < 0:
            raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, CustomErrorMessage(
                                OrderErrorMessageEnum.ITEM_OUT_OF_STOCK, error_message="Item out of stock", error_detail=f"Product: {product_ordered.id}").jsonify()
                                )
    if total_cost == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            CustomErrorMessage(
                                OrderErrorMessageEnum.NO_COST_CALCULATED, error_message="You cant checkout with no items"))
    # add delivery fee,tip
    calculated_delivery_fee = calculate_address_delivery_fee(order.address_id)
    delivery_fee = calculated_delivery_fee['delivery_charge'] - \
        calculated_delivery_fee['discount']
    total_cost += delivery_fee
    total_cost += order.tip_amount
    # check to see if user has credit
    credit_used = 0
    if current_user.credit > 0:
        if current_user.credit > total_cost:
            credit_used = total_cost
            total_cost = 0
        else:
            total_cost -= current_user.credit
            credit_used = current_user.credit
    # user is using a valid promo code
    # if promo_code_credit:
    #     total_cost -= promo_code_credit
    #     if total_cost < 0:
    #         total_cost = 0
    # If credit is larger then cost, dont return payment_intent/stripe ephemeral key
    if total_cost == 0:
        payment_intent = None
        stripe_ephemeral_key = None
    else:
        if total_cost < MIN_ORDER_THRESHOLD:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                CustomErrorMessage(
                                    OrderErrorMessageEnum.COST_LESS_THEN_THRESHOLD, error_message=f"You cant checkout with less then {MIN_ORDER_THRESHOLD} cents"))
        payment_intent = StripeApiClient('cad').generate_payment_intent(
            current_user.stripe_id, total_cost)
        stripe_ephemeral_key = StripeApiClient('cad').generate_ephemeral_key(
            current_user.stripe_id)
    # create new order
    new_order = Order(user_id=current_user.id, cost=total_cost, delivery_charge=delivery_fee, tax_charge=total_tax,
                      status=OrderStatusEnum.checking_out, tip_amount=order.tip_amount, subtotal=subtotal, credit_used=credit_used)
    # Link promo code if exists
    # if promo_code_credit:
    #     new_order.promo_code_id = promo_code_targeted.id
    #     promo_code_targeted.num_redeems_allowed -= 1
    #     promo_code_targeted.orders.append(new_order)
    if payment_intent:
        new_order.stripe_payment_intent = payment_intent.id
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
    return {"id": new_order.id,
            "cost":  new_order.cost,
            "subtotal": subtotal,
            "tip_amount": order.tip_amount,
            "tax_charge": total_tax,
            "delivery_charge": delivery_fee,
            "stripe_payment_intent_secret": payment_intent.client_secret if payment_intent else None,
            'stripe_customer_id': current_user.stripe_id,
            'stripe_ephemeral_key': stripe_ephemeral_key.secret if stripe_ephemeral_key else None,
            # 'promo_code': promo_code_targeted.promo_code if promo_code_targeted else None,
            'credit_used': credit_used}


@ router.put('/{order_id}/confirm')
def post_orders(order_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    """This function is only used when a user has more credit then cost.
    In this case we completely forego stripe and use all of the customer's credit
    """
    targeted_order = session.query(Order).filter_by(
        cost=0, user_id=current_user.id, status=OrderStatusEnum.checking_out).filter(Order.credit_used > 0).first()
    if targeted_order is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            CustomErrorMessage(
                                OrderErrorMessageEnum.NO_CREDIT_ORDER_FOUND, error_message="Order completely paid in credit not found", error_detail="We cant find an order that the user made that was completely paid in credit").jsonify())
    # change status, remove credit, generate slack, write push
    datetime_now = datetime.datetime.utcnow()
    targeted_order.status = OrderStatusEnum.paid
    current_user.credit -= targeted_order.credit_used
    if current_user.apn_token:
        send_push_sns(current_user.apn_token, "ios",
                      generate_apple_order_push_payload("⚡️ Thanks for your order!️", "Our team will begin preparing your order shortly.", OrderStatusEnum.paid))
    if current_user.fcm_token:
        send_push_sns(current_user.fcm_token, "android",
                      "⚡️ Thanks for your order!️ Our team will begin preparing your order shortly.")
    targeted_order.date_paid = datetime_now
    session.commit()
    SlackWebhookClient().post_delivery(targeted_order.id, targeted_order.user,
                                       targeted_order.address, targeted_order.products_ordered)
    return status.HTTP_200_OK
