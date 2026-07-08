from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ToolResponse
from app import crud, services

# APIRouter groups related routes. Prefix and tags are set in main.py.
router = APIRouter(tags=["tools"])


@router.post("/sync", status_code=status.HTTP_202_ACCEPTED)
def sync_stars(background_tasks: BackgroundTasks):
    """
    POST /tools/sync — Refresh every tool's GitHub star count.

    The actual fetching runs in a background task, so this returns 202 Accepted
    immediately; the star counts and each tool's last_synced_at timestamp are
    updated once the task finishes. Poll GET /tools/ to observe the result.
    """
    background_tasks.add_task(services.sync_all_tool_stars)
    return {"status": "sync scheduled"}


@router.get("/", response_model=list[ToolResponse])
def list_tools(db: Session = Depends(get_db)):
    """
    GET /tools — Returns all tools in the database.

    response_model=list[ToolResponse] tells FastAPI to:
      - Filter the ORM objects through the ToolResponse schema
      - This strips any fields not in the schema (security best practice)
      - Automatically generates the correct OpenAPI documentation
    """
    tools = crud.get_all_tools(db)
    return tools


@router.get("/{tool_id}", response_model=ToolResponse)
def get_tool(tool_id: str, db: Session = Depends(get_db)):
    """
    GET /tools/{tool_id} — Returns a single tool with its rating stats.

    {tool_id} is a path parameter — FastAPI extracts it from the URL.
    Example: GET /tools/pytest  →  tool_id = "pytest"
    """
    tool = crud.get_tool_by_id(db, tool_id)

    if tool is None:
        # 404 Not Found — standard HTTP response for missing resources
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_id}' not found",
        )

    # Combine the tool ORM object with the stats dict into a response
    return ToolResponse(
        id=tool.id,
        name=tool.name,
        category=tool.category,
        description=tool.description,
        github_stars=tool.github_stars
    )
