from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from schemas.UserSchema import UserSchemaOut, UserSchemaIn, UserSchemaPut, UserPhoneNumberPut, UserPaymentMethods, ReferralCodeIn
# Models
from models.Rider import Rider
from models.Order import Order, OrderStatusEnum
from models.S3StaticFileClient import S3StaticFileClient
from models.CustomErrorMessage import UserErrorMessageEnum, CustomErrorMessage
# Auth
from auth import get_current_rider
from utils import serialize, validate_id_querystring
# schemas
from schemas.RiderSchema import RiderSchemaOut
from schemas.OrderSchema import OrderSchemaOut
# utils
from database import get_db
from starlette.responses import JSONResponse

router = APIRouter()


@router.get('', response_model=RiderSchemaOut)
def retrieve_rider_data(current_rider: Rider = Depends(get_current_rider), session: Session = Depends(get_db)):
    return serialize(current_rider)


@router.get('/current_orders', response_model=List[OrderSchemaOut])
def retrieve_current_order(current_rider: Rider = Depends(get_current_rider), session: Session = Depends(get_db)):
    current_orders = session.query(Order).filter(Order.rider_assigned_id == current_rider.id).filter(
        Order.status.in_([OrderStatusEnum.preparing, OrderStatusEnum.paid, OrderStatusEnum.out_for_delivery, OrderStatusEnum.delivered])).all()
    # no current order
    if len(current_orders) == 0:
        return []
    return_orders = []
    for current_order in current_orders:
        order = serialize(current_order)
        order['products_ordered'] = [
            serialize(x) for x in current_order.products_ordered]
        return_orders.append(order)
    return return_orders
