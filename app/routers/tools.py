from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ToolResponse
from app import crud

# APIRouter groups related routes. Prefix and tags are set in main.py.
router = APIRouter(tags=["tools"])


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
