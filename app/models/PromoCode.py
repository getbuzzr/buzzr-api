from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Boolean
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref


class PromoCode(Base):
    """Base Promo Code """

    __tablename__ = "promo_code"

    id = Column(Integer, primary_key=True)
    promo_code = Column(String(100))
    credit = Column(Integer)
    orders = relationship('Order', backref='promo_code',
                          lazy='dynamic')
    valid_until = Column(DateTime)
    valid_from = Column(DateTime)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    num_redeems_allowed = Column(Integer)
    only_first_order = Column(Boolean)
