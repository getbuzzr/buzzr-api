from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum, SmallInteger, Text
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum
from utils import serialize


class RecipeItemTypeEnum(str, enum.Enum):
    required = "required"
    things_you_may_have = 'things_you_may_have'
    substitution = 'substitution'


class RecipeItem(Base):
    """Base Recipe Model
    """
    __tablename__ = "recipe_item"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    quantity = Column(Integer)
    recipe_item_type = Column(Enum(RecipeItemTypeEnum),
                              server_default=("required"))
