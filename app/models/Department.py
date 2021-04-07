from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref


class Department(Base):
    """Base Department """

    __tablename__ = "department"

    id = Column(Integer, primary_key=True)
    picture_url = Column(String(400))
    name = Column(String(100))
    categories = relationship(
        'Category', backref=backref('department'))
