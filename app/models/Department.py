from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Boolean
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
    is_active = Column(Boolean, default=True,
                       server_default="1", nullable=False)
    categories = relationship(
        'Category', backref=backref('department'))
