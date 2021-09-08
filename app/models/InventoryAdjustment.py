from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum, SmallInteger
from sqlalchemy.sql.elements import Null
from database import Base
import logging
import datetime
from sqlalchemy.orm import relationship, backref
import enum


class AdjustmentReason(str, enum.Enum):
    spoilage = 'spoilage'
    damage = 'damage'
    inventory_error = 'inventory_error'
    theft = 'theft'
    delivery_error = 'delivery_error'
    writeoff = 'writeoff'

class InventoryAdjustment(Base):
    """Base Inventory Adjustment
    """
    __tablename__ = "inventory_adjustment"

    id = Column(Integer, primary_key=True)
    # quantity can be positive or negative for found product or for shrink respectively
    quantity = Column(SmallInteger)
    date_adjusted = Column(DateTime, default=datetime.date.today)
    product_id = Column(Integer, ForeignKey('product.id'))
    reason = Column(Enum(AdjustmentReason))