from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Boolean, Enum
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum


class DeliveryPreferenceEnum(enum.Enum):
    leave_at_door = "leave at door"
    buzz_up = 'buzz_up'
    call_upon_arrival = 'call_upon_arrival'
    meet_downstairs = 'meet_downstairs'


class Address(Base):
    """Base Category """

    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    user_id = Column(Integer, ForeignKey('user.id'))
    street_address = Column(String(100))
    apartment_number = Column(String(30))
    buzzer = Column(String(20))
    postal_code = Column(String(20))
    province = Column(String(20))
    country = Column(String(50))
    is_default = Column(Boolean)
    additional_instructions = Column(String(200))
    delivery_preference = Column(
        Enum(DeliveryPreferenceEnum))
