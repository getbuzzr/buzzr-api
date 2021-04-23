from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref


class ProductSuggestion(Base):
    """Base Department """

    __tablename__ = "product_suggestion"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    user_id = Column(Integer, ForeignKey('user.id'))
