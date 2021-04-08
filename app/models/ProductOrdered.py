from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum, SmallInteger
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum


class ProductOrdered(Base):
    """Base Product Ordered
    """
    __tablename__ = "product_ordered"

    id = Column(Integer, primary_key=True)
    quantity = Column(SmallInteger)
    date_ordered = Column(DateTime, default=datetime.datetime.utcnow)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
