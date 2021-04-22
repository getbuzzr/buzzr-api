from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Enum, Float, Boolean
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum


class StarRatingEnum(enum.Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5


class OrderStatusEnum(enum.Enum):
    failed = "failed"
    checking_out = "checking_out"
    paid = "paid"
    preparing = "preparing"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    arrived = "arrived"
    complete = "complete"


class Order(Base):
    """order"""

    __tablename__ = "order"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    products_ordered = relationship(
        'ProductOrdered', backref=backref('order'))
    feedback = Column(String(200))
    stars = Column(Enum(StarRatingEnum))
    cost = Column(Float)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    date_delivered = Column(DateTime)
    last_updated = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    status = Column(Enum(OrderStatusEnum), server_default="checking_out")
    stripe_payment_intent = Column(String(30))
    address_id = Column(Integer, ForeignKey('address.id'))
    latitude = Column(Float)
    longitude = Column(Float)
    additional_instruction = Column(String(200))
    refund_requested = Column(Boolean, default=False)
