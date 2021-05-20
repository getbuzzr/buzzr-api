from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Boolean, Enum, Float
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum


class DeliveryPreferenceEnum(str, enum.Enum):
    leave_at_door = "leave_at_door"
    buzz_up = 'buzz_up'
    call_upon_arrival = 'call_upon_arrival'
    meet_downstairs = 'meet_downstairs'


class AddressStatusEnum(str, enum.Enum):
    active = "active"
    deleted = "deleted"


class Address(Base):
    """Base Category """

    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    user_id = Column(Integer, ForeignKey('user.id'))
    street_address = Column(String(100), nullable=False)
    apartment_number = Column(String(30))
    buzzer = Column(String(20))
    postal_code = Column(String(20))
    province = Column(String(20), nullable=False)
    city = Column(String(50), nullable=False, default="Vancouver")
    country = Column(String(50), nullable=False)
    is_default = Column(Boolean)
    latitude = Column(Float, nullable=False, default=0)
    longitude = Column(Float, nullable=False, default=0)
    additional_instructions = Column(String(200))
    delivery_preference = Column(
        Enum(DeliveryPreferenceEnum))
    status = Column(
        Enum(AddressStatusEnum), server_default=("active"))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, default=datetime.datetime.utcnow)
    orders = relationship(
        'Order', backref=backref('address'))
    is_serviceable = Column(Boolean, default=False)
    seconds_away_from_hq = Column(Integer)
    google_share_url = Column(String(250))
