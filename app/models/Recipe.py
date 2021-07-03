from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum, SmallInteger, Text
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum
from utils import serialize


class Recipe(Base):
    """Base Recipe Model
    """
    __tablename__ = "recipe"

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    instructions = Column(Text)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    image_url = Column(String(300))
    recipe_items = relationship(
        "RecipeItem", backref=backref('recipe', lazy="select"))
    active_time_seconds = Column(Integer)
    total_time_seconds = Column(Integer)
    servings = Column(Integer)
    calories = Column(Integer)
    description = Column(String(500))
