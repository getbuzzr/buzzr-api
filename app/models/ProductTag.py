from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Boolean, SmallInteger
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref


class ProductTag(Base):
    """Base Category """

    __tablename__ = "product_tag"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    is_featured = Column(Boolean, default=False)
    order = Column(SmallInteger)
    display_morning = Column(Boolean)
    display_afternoon = Column(Boolean)
    display_evening = Column(Boolean)
    display_night = Column(Boolean)
