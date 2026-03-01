from pydantic import BaseModel, Field


class ToolResponse(BaseModel):
    """What the API sends back when you ask for a tool."""
    id: str
    name: str
    category: str
    description: str | None = None
    github_stars: int = 0

    class Config:
        # Allow creating this schema directly from an ORM model object
        from_attributes = True

class HealthResponse(BaseModel):
    """Response shape for the /health endpoint."""
    status: str          # "ok" or "error"
    database: str        # "connected" or "disconnected"
