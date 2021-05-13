from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Enum, Float, Boolean
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum


class StarRatingEnum(str, enum.Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5


class OrderStatusEnum(str, enum.Enum):
    failed = "failed"
    checking_out = "checking_out"
    paid = "paid"
    preparing = "preparing"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    complete = "complete"
    refunded = "refunded"


class Order(Base):
    """order"""

    __tablename__ = "order"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    products_ordered = relationship(
        'ProductOrdered', backref=backref('order'))
    feedback = Column(String(200))
    stars = Column(Enum(StarRatingEnum))
    cost = Column(Integer)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    date_delivered = Column(DateTime)
    date_preparing = Column(DateTime)
    date_out_for_delivery = Column(DateTime)
    date_complete = Column(DateTime)
    date_failed = Column(DateTime)
    date_paid = Column(DateTime)
    tip_amount = Column(Integer, default=0)
    subtotal = Column(Integer)
    last_updated = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    status = Column(Enum(OrderStatusEnum), server_default="checking_out")
    stripe_payment_intent = Column(String(30))
    address_id = Column(Integer, ForeignKey('address.id'))
    latitude = Column(Float)
    longitude = Column(Float)
    additional_instruction = Column(String(200))
    refund_requested = Column(Boolean, default=False)
    delivery_charge = Column(Integer)
    tax_charge = Column(Integer)
    credit_used = Column(Integer)
