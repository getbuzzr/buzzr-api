from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref


class Coupon(Base):
    """Base coupon """

    __tablename__ = "coupon"

    id = Column(Integer, primary_key=True)
    coupon_code = Column(String(100))
    credit = Column(Integer)
    valid_until = Column(DateTime)
    valid_from = Column(DateTime)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
