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

    transaction_id = Column(Integer, primary_key=True)
    quantity = Column(SmallInteger)
    date_purchased = Column(DateTime, default=datetime.date.today)
    product_id = Column(Integer, ForeignKey('product.id'))
    # price is in cents
    purchase_price = Column(Integer)
    tax = Column(Float,default=0)
    date_expiry = Column(DateTime, default=None)
    location_purchased = Column(String)