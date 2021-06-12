from models.Order import Order, OrderStatusEnum
from routers.orders import re_add_stock
from database import session_scope
import datetime
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from utils import serialize, send_push_sns, generate_apple_order_push_payload


def remove_abandoned_orders():
    print("START ABANDON ORDER")
    with session_scope() as session:
        # get all orders that are checking out date_created > 5 mins ago
        ten_mins_since = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
        thirty_mins_since = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        orders_ten_mins_over = session.query(Order).filter(and_(Order.status == OrderStatusEnum.checking_out,
                                                                Order.date_created < ten_mins_since)).all()
        for order_ten_min_over in orders_ten_mins_over:
            # user has not been push notified, send push
            if not order_ten_min_over.is_user_abandoned_cart_notified:
                user = order_ten_min_over.user
                # TODO WRITE GOOD PUSH COPY
                # if user.apn_token:
                #     send_push_sns(user.apn_token, "ios",
                #                   generate_apple_order_push_payload("Looks like you are still checking out", "", OrderStatusEnum.paid))
                # if user.fcm_token:
                #     send_push_sns(user.fcm_token, "android",
                #                   "Looks like you are still checking out some items. Click here to finish your checkout!")
                order_ten_min_over.is_user_abandoned_cart_notified = True
                session.add(order_ten_min_over)
                continue
            # if order is 30 mins over, delete
            if order_ten_min_over.date_created < thirty_mins_since:
                re_add_stock(order_ten_min_over, session)
                session.delete(order_ten_min_over)
        session.commit()
        session.close()
