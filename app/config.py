import os

DATABASE_URL = os.getenv("DATABASE_URL") or (
    "postgresql://"
    f"{os.getenv('DB_USER', 'postgres')}:"
    f"{os.getenv('DB_PASS', 'postgres')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:"
    f"{os.getenv('DB_PORT', '5432')}/"
    f"{os.getenv('DB_NAME', 'devops_rating')}"
)
