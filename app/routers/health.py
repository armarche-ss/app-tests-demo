from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Returns the health status of the application.

    Checks:
      1. Is the app running? (if we get here, yes)
      2. Can we query the database? (runs a trivial SQL query)

    Returns HTTP 200 with {"status": "ok"} if everything is fine.
    Returns HTTP 200 with {"status": "error"} if the DB is down
    (we return 200 so the container keeps running — alerting is separate).
    """
    try:
        # Execute a minimal query — if this doesn't raise, DB is reachable
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="ok" if db_status == "connected" else "error",
        database=db_status,
    )
