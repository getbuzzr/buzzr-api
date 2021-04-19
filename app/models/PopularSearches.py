from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref


class PopularSearches(Base):
    """Base Department """

    __tablename__ = "popular_searches"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
