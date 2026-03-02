from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Tool


# ---------------------------------------------------------------------------
# Tool queries
# ---------------------------------------------------------------------------

def get_all_tools(db: Session) -> list:
    """Returns all tools from the database, ordered alphabetically."""
    return db.query(Tool).order_by(Tool.name).all()


def get_tool_by_id(db: Session, tool_id: str):
    """
    Returns a single Tool by its id, or None if not found.

    db.query(Tool) → start a SELECT on the tools table
    .filter(...)   → add a WHERE clause
    .first()       → return the first result or None
    """
    return db.query(Tool).filter(Tool.id == tool_id).first()
