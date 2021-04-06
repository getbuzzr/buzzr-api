from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref


class ProductTag(Base):
    """Base Category """

    __tablename__ = "product_tag"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
