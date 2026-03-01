from fastapi import FastAPI

from app.database import engine, Base
from app.routers import health, tools

app = FastAPI(
    title="DevOps Tools Rating API",
    description="Rate and discover open-source tools used by DevOps engineers.",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(tools.router, prefix="/tools")


@app.get("/")
def root():
    """Root endpoint — a friendly welcome message."""
    return {
        "message": "DevOps Tools Rating API",
        "docs": "/docs",
        "health": "/health",
    }
