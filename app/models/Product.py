from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum, SmallInteger
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum
from utils import serialize
product_tags = Table('product_tags', Base.metadata,
                     Column(
                         'product_id', Integer, ForeignKey('product.id')),
                     Column('tag_id', Integer, ForeignKey('product_tag.id')),
                     Column('date_created', DateTime,
                            default=datetime.datetime.utcnow))


class ProductUnitEnum(str, enum.Enum):
    weight = "weight"
    pack = 'pack'
    volume = 'volume'
    piece = 'piece'


class ProductStatusEnum(str, enum.Enum):
    active = "active"
    deleted = "deleted"
    hidden = "hidden"


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
    quantity = Column(Integer)
    cost = Column(Integer)
    tax = Column(Float, default=0)
    percent_discount = Column(Integer, default=0)
    image_url = Column(String(300))
    shelf_number = Column(SmallInteger)
    unit = Column(
        Enum(ProductUnitEnum), server_default="weight")
    status = Column(
        Enum(ProductStatusEnum), server_default=("active"))
    tags = relationship(
        'ProductTag', secondary=product_tags, backref=backref('product'))
    product_ordered = relationship(
        "ProductOrdered", backref=backref('product', lazy="select"))

    def serialize_product(self):
        product = serialize(self)
        product['tags'] = [serialize(x) for x in self.tags]
        return product
