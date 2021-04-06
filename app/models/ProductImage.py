from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum


class ProductImage(Base):
    """Base Product Image
    """
    __tablename__ = "product_image"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    title = Column(String(200))
    date_added = Column(
        DateTime, default=datetime.datetime.utcnow)
    image_url = Column(String(400))
