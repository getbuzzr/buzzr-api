from sqlalchemy import create_engine
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

# initialize db env
engine = create_engine(os.environ.get(
    'SQLALCHEMY_DATABASE_URI'), pool_pre_ping=True, pool_size=32, max_overflow=64)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()
metadata = Base.metadata


def get_db():
    try:
        db = SessionLocal()
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def session_scope():
    try:
        db = SessionLocal()
        yield db
    except:
        db.rollback()
    finally:
        db.close()
