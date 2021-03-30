from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum


class UserRoleEnum(enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    user = 'user'


class User(Base):
    """Base User Model
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    cognito_sub = Column(String(36), nullable=True)
    email = Column(String(50), nullable=False, unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    address = Column(String(300))
    postal_code = Column(String(30))
    city = Column(String(30))
    country = Column(String(30))
    additional_information = Column(String(200))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    apn_token = Column(String(100))
    fcm_token = Column(String(100))
    profile_picture_url = Column(String(150))

    def is_admin(self):
        """Check to see if user is an admin
        @returns Boolean
        """
        if self.role.value in ['admin', 'super_admin']:
            return True
        return False

    def is_super_admin(self):
        """Check to see if user is super admin
        @returns Boolean
        """
        if self.role.value == "super_admin":
            return True
        return False
