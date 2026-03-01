import os
import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base   # SQLAlchemy 2.0 location
from sqlalchemy.exc import OperationalError

from .config import DATABASE_URL

logger = logging.getLogger(__name__)


# Build the correct engine for the current DATABASE_URL.
# SQLAlchemy is lazy — it won't actually open a connection until a query runs.
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all ORM model classes (see models.py)
# SQLAlchemy 2.0: import declarative_base from sqlalchemy.orm, not ext.declarative
Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yields one database session per request.

    FastAPI calls this before the route handler and closes the session
    after the response is sent, even if an exception occurred.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
