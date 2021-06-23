from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, Boolean
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref


class Category(Base):
    """Base Category """

    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    is_active = Column(Boolean, default=True,
                       server_default="1", nullable=False)
    department_id = Column(Integer, ForeignKey('department.id'))
    products = relationship(
        'Product', backref=backref('category'))
