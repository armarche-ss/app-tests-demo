"""
config.py — Application configuration
======================================
All settings are read from environment variables.
This is the standard 12-factor app approach: configuration lives outside
the code so the same Docker image can run in dev, test, and production.

The environment variables are defined in docker-compose.yml.
"""
import os

# ---------------------------------------------------------------------------
# Database connection settings
# Each value has a sensible default for local development without Docker.
# ---------------------------------------------------------------------------

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")      # Standard PostgreSQL port
DB_NAME = os.getenv("DB_NAME", "devops_tools")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# ---------------------------------------------------------------------------
# Build the full connection URL from the individual parts above.
# SQLAlchemy uses this URL to connect to the database.
# Format: postgresql://user:password@host:port/dbname
# ---------------------------------------------------------------------------
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
