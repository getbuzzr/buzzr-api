from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum

favorite_products = Table('favorite_products', Base.metadata,
                          Column(
                              'product_id', Integer, ForeignKey('product.id')),
                          Column('user_id', Integer, ForeignKey('user.id')),
                          Column('date_created', DateTime,
                                 default=datetime.datetime.utcnow))


class UserRoleEnum(str, enum.Enum):
    admin = "admin"
    user = 'user'


class User(Base):
    """Base User Model
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    cognito_sub = Column(String(36))
    email = Column(String(50), nullable=False, unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    additional_information = Column(String(200))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, default=datetime.datetime.utcnow)
    apn_token = Column(String(100))
    fcm_token = Column(String(100))
    profile_picture_url = Column(String(400))
    referral_id = Column(String(10))
    referrer_id = Column(Integer)
    stripe_id = Column(String(20))
    phone_verification_code = Column(String(5))
    is_phone_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRoleEnum), nullable=False, server_default="user")
    favorite_products = relationship(
        'Product', secondary=favorite_products, backref=backref('favorited_by'))
    addresses = relationship(
        'Address', backref=backref('user'))
    orders = relationship(
        'Order', backref=backref('user'))

    def is_admin(self):
        """Check to see if user is super admin
        @returns Boolean
        """
        if self.role.value == "admin":
            return True
        return False
