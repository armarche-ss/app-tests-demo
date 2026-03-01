"""
config.py — Application configuration
======================================
All settings are read from environment variables.
This is the standard 12-factor app approach: configuration lives outside
the code so the same Docker image can run in dev, test, and production.

The environment variables are defined in docker-compose.yml.
"""
import os

DATABASE_URL = os.getenv("DATABASE_URL") or (
    "postgresql://"
    f"{os.getenv('DB_USER', 'postgres')}:"
    f"{os.getenv('DB_PASS', 'postgres')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:"
    f"{os.getenv('DB_PORT', '5432')}/"
    f"{os.getenv('DB_NAME', 'devops_rating')}"
)
