from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum, SmallInteger
from sqlalchemy.sql.elements import Null
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum


class ProductSold(Base):
    """Base Product Sold
    """
    __tablename__ = "product_sold"

    id = Column(Integer, primary_key=True)
    quantity = Column(SmallInteger)
    date_sold = Column(DateTime, default=datetime.datetime.utcnow)
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    sale_price_cents = Column(Integer)
    tax = Column(Float,default=0)
    discout = Column(Float,default=0)