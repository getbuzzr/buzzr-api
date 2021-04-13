from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.Order import Order, OrderStatusEnum
from models.User import User
from models.Product import Product
from models.ProductOrdered import ProductOrdered

# Schemas
from schemas.OrderSchema import OrderSchemaOut, OrderSchemaIn, OrderSchemaCreateOut, AdminOrderSchemaEdit
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


@router.put('/orders/{order_id}', response_model=OrderSchemaOut)
def put_orders(order: AdminOrderSchemaEdit, order_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    edited_order = session.query(Order).get(order_id)
    if edited_order is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"User: {order_id} doesnt exist")
    # iterate through all the attributes of the usereditschema
    for key, value in order.dict().items():
        # If key is being edited
        if value:
            setattr(edited_order, key, value)
    # if status is updated, send a push
    if 'status' in order.dict().keys():
        targeted_user = session.query(User).get(edited_order.user_id)
        if targeted_user.apn_token:
            send_push_sns(targeted_user.apn_token, "ios", "hello Brandon")
        if targeted_user.fcm_token:
            send_push_sns(targeted_user.fcm_token, "android", "hello Brandon")
    # push edits
    session.commit()
    return_edit_order = serialize(edited_order)
    return_edit_order['products_ordered'] = [
        serialize(x) for x in order.products_ordered]
    return return_edit_order
