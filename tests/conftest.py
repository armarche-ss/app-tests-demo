"""
tests/conftest.py — Shared pytest fixtures for all test types.

DATABASE ISOLATION STRATEGY:
──────────────────────────────────────────────────────────────────────
  The two problems this file solves:

  Problem 1 — Seed data pollution:
    main.py seeds 15 tools into the database on startup. If tests connect
    to the same `devops_rating` database, `test_empty_database_returns_empty_list`
    will always fail (it finds 15 rows instead of 0).

    Fix: tests use a SEPARATE database named `devops_rating_test`.
    The app startup event never touches this database, so tests always
    start with a clean, unseeded schema.

  Problem 2 — Duplicate key errors across tests:
    session.rollback() only undoes changes made in the CURRENT session that
    haven't been committed yet. Once a fixture calls session.commit(), that
    data is permanent until explicitly deleted. The next test's fixture then
    tries to INSERT the same primary key and gets a UniqueViolation.

    Fix: the db_session fixture deletes all rows from every table after
    each test, regardless of whether the test committed or rolled back.

DATABASE SELECTION:
──────────────────────────────────────────────────────────────────────
  DATABASE_URL MUST be set before importing any app module.
  app/database.py reads it at import time to build its engine.
  We set it here at the very top of conftest.py, which pytest loads first.

  Locally (no Docker):   SQLite, no setup needed.
  In Docker tests container (TEST_USE_POSTGRES=1): devops_rating_test
──────────────────────────────────────────────────────────────────────
"""

import os

# # ---------------------------------------------------------------------------
# # Step 1 — Determine and set DATABASE_URL BEFORE any app imports.
# #
# # If we don't do this first, `from app.main import app` triggers
# # app/database.py which tries to TCP-connect to PostgreSQL immediately.
# # ---------------------------------------------------------------------------


os.environ["DATABASE_URL"] = "sqlite:///./test.db"
# ---------------------------------------------------------------------------
# Step 2 — Now it is safe to import app modules.
#           database.py will read DATABASE_URL from os.environ above.
# ---------------------------------------------------------------------------

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
_connect_args = {"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(TEST_DATABASE_URL, connect_args=_connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """
    Create all tables once at the start of the test session, drop them at the end.

    scope="session" — runs once for the entire pytest run.
    autouse=True    — applied to every test automatically.

    Because we use a separate test database (`devops_rating_test`), these
    tables are always empty at the start — no seed data from the app.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """
    Provides a database session for each test, with full cleanup afterwards.

    WHY NOT JUST ROLLBACK?
      session.rollback() only undoes changes that haven't been committed yet
      in this session. If a fixture calls session.commit() (which is required
      to make data visible to the TestClient), those rows are permanent until
      explicitly deleted.

      Simply rolling back would leave committed rows in the table, causing
      the next test's INSERT to fail with UniqueViolation.

    THE FIX:
      After each test we DELETE all rows from every table. This is safe
      because we're in the test database, not the production database.
      The next test always starts with empty tables.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()  # Undo any uncommitted changes from the test itself

        # Delete all data from every table in dependency order (children first)
        # so foreign key constraints are not violated.
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture()
def client(db_session):
    """
    Provides a FastAPI TestClient that uses the test database session.

    FastAPI's dependency_overrides replaces get_db() so that every database
    call inside the app uses our test session instead of the production one.
    This means the full HTTP → router → crud → database path is exercised,
    but against our isolated test database.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()