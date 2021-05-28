from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum
from uuid import uuid4


class Rider(Base):
    """Base User Model
    """
    __tablename__ = "rider"

    id = Column(Integer, primary_key=True)
    cognito_sub = Column(String(36))
    email = Column(String(50), nullable=False, unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    phone_country_code = Column(String(5))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, default=datetime.datetime.utcnow)
    apn_token = Column(String(100))
    fcm_token = Column(String(100))
    profile_picture_url = Column(String(400))
    orders = relationship(
        'Order', backref=backref('rider'))
