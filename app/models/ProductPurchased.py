from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum, SmallInteger
from sqlalchemy.sql.elements import Null
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum


class ProductPurchased(Base):
    """Base Product Purchased
    """
    __tablename__ = "product_purchased"

    id = Column(Integer, primary_key=True)
    quantity = Column(SmallInteger)
    date_purchased = Column(DateTime, default=datetime.date.today)
    product_id = Column(Integer, ForeignKey('product.id'))
    purchase_price_cents = Column(Integer)
    tax = Column(Float,default=0)
    date_expiry = Column(DateTime)
    location_purchased = Column(String(200))