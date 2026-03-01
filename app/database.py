import os
import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base   # SQLAlchemy 2.0 location
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Database URL — supports a full override via DATABASE_URL env var.
#
# When running normally (in Docker), DATABASE_URL is not set, so we build
# the PostgreSQL URL from the individual DB_* variables set in docker-compose.
#
# When running tests locally, conftest.py sets DATABASE_URL to a SQLite URL
# before importing this module, so the PostgreSQL URL is never constructed.
# ---------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL") or (
    "postgresql://"
    f"{os.getenv('DB_USER', 'postgres')}:"
    f"{os.getenv('DB_PASS', 'postgres')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:"
    f"{os.getenv('DB_PORT', '5432')}/"
    f"{os.getenv('DB_NAME', 'devops_rating')}"
)


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
