from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, Boolean, Enum
from database import Base


class Search(Base):
    """Search Terms
    """
    __tablename__ = "search"

    id = Column(Integer, primary_key=True)
    search_term = Column(String(100))
