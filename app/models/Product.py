from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum

product_tags = Table('product_tags', Base.metadata,
                     Column(
                         'product_id', Integer, ForeignKey('product.id')),
                     Column('tag_id', Integer, ForeignKey('product_tag.id')),
                     Column('date_created', DateTime,
                            default=datetime.datetime.utcnow))


class Product(Base):
    """Base Product Model
    """
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    name = Column(String(200))
    stock = Column(Integer)
    description = Column(String(300))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    department_id = Column(Integer, ForeignKey('department.id'))
    last_updated = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    weight = Column(Integer)
    cost = Column(Float)
    tags = relationship(
        'ProductTag', secondary=product_tags, backref=backref('product'))
    pictures = relationship(
        'ProductImage', backref=backref('product'))
