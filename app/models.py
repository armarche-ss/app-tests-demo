from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Index
from sqlalchemy.sql import func

from app.database import Base


class Tool(Base):
    """
    Represents one DevOps tool (e.g., pytest, Docker, Terraform).

    Table name: tools
    """
    __tablename__ = "tools"

    # Primary key — a short slug like "pytest" or "docker-compose"
    id = Column(String(64), primary_key=True, index=True)

    # Human-readable display name
    name = Column(String(128), nullable=False)

    # Top-level grouping (e.g., "Testing", "Containers", "IaC")
    category = Column(String(64), nullable=False)

    # One-sentence description shown in the UI
    description = Column(Text, nullable=True)

    # Number of GitHub stars — for sorting / reference
    github_stars = Column(Integer, default=0)

    # GitHub repository slug ("owner/name") — used to build the API URL we sync
    # stars from and the link the UI star icon opens.
    github_repo = Column(String(128), nullable=True)

    # When the star count was last refreshed from the GitHub API.
    # NULL means "never synced". Set by the background sync task.
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
