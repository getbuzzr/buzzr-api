from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref


class PopularSearch(Base):
    """Base Department """

    __tablename__ = "popular_search"

    id = Column(Integer, primary_key=True)
    query = Column(String(100))
