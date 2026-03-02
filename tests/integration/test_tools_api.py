import pytest
from fastapi.testclient import TestClient

from app.models import Tool


# ---------------------------------------------------------------------------
# Fixtures — insert test data into the clean database
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_tool(db_session):
    """
    Inserts one Tool and returns it.

    The db_session fixture (conftest.py) deletes all rows after each test,
    so this tool is automatically cleaned up — no manual teardown needed.
    """
    tool = Tool(
        id="pytest",
        name="pytest",
        category="Testing",
        description="The most popular Python testing framework.",
        github_stars=12400,
    )
    db_session.add(tool)
    db_session.commit()
    return tool


@pytest.fixture
def multiple_tools(db_session):
    """Inserts three tools for tests that need a populated database."""
    tools = [
        Tool(id="docker",     name="Docker",     category="Containers",    description="The container runtime.", github_stars=69000),
        Tool(id="prometheus", name="Prometheus",  category="Observability", description="Pull-based metrics.",    github_stars=56200),
        Tool(id="terraform",  name="Terraform",   category="IaC",           description="Infrastructure as code.", github_stars=43700),
    ]
    for t in tools:
        db_session.add(t)
    db_session.commit()
    return tools


# =============================================================================
# Tests — GET /tools/
# =============================================================================

class TestListTools:

    def test_empty_database_returns_empty_list(self, client: TestClient):
        """
        When no tools have been inserted, /tools/ returns an empty list.

        This works because conftest.py uses a separate `devops_rating_test`
        database that the app's startup seed event never touches. Every test
        starts with empty tables.
        """
        response = client.get("/tools/")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_inserted_tool(self, client: TestClient, sample_tool):
        """
        After inserting one tool, GET /tools/ returns exactly that tool.
        Proves the full write → read path through the real database works.
        """
        response = client.get("/tools/")

        assert response.status_code == 200
        tools = response.json()
        assert len(tools) == 1
        assert tools[0]["id"]       == "pytest"
        assert tools[0]["name"]     == "pytest"
        assert tools[0]["category"] == "Testing"

    def test_returns_all_inserted_tools(self, client: TestClient, multiple_tools):
        """All inserted tools are returned."""
        response = client.get("/tools/")

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_tools_returned_in_alphabetical_order(self, client: TestClient, multiple_tools):
        """
        Tools must be returned in alphabetical order by name.
        This test will fail if ordering is broken (e.g., ordered by ID or category).
        """
        response = client.get("/tools/")
        
        assert response.status_code == 200
        tools = response.json()
        names = [t["name"] for t in tools]
        
        # Expected alphabetical order: Docker, Prometheus, Terraform
        assert names == ["Docker", "Prometheus", "Terraform"], \
            f"Tools not in alphabetical order. Got: {names}"

    def test_response_schema_shape(self, client: TestClient, sample_tool):
        """
        Each tool in the response has exactly the expected fields.
        Catches additions to or removals from ToolResponse.
        """
        response = client.get("/tools/")
        tool = response.json()[0]

        # Fields that must be present
        assert "id"           in tool
        assert "name"         in tool
        assert "category"     in tool
        assert "description"  in tool
        assert "github_stars" in tool

        # Fields that were removed — confirm they're gone
        assert "subcategory"    not in tool
        assert "average_rating" not in tool
        assert "total_ratings"  not in tool


# =============================================================================
# Tests — GET /tools/{tool_id}
# =============================================================================

class TestGetTool:

    def test_get_existing_tool_returns_200(self, client: TestClient, sample_tool):
        """GET /tools/pytest returns 200 with the correct data."""
        response = client.get("/tools/pytest")

        assert response.status_code == 200
        data = response.json()
        assert data["id"]           == "pytest"
        assert data["name"]         == "pytest"
        assert data["category"]     == "Testing"
        assert data["github_stars"] == 12400

    def test_get_nonexistent_tool_returns_404(self, client: TestClient):
        """
        Requesting a tool that doesn't exist returns 404 Not Found.
        Verifies the route handles the missing-resource case correctly.
        """
        response = client.get("/tools/this-tool-does-not-exist")

        assert response.status_code == 404

    def test_description_can_be_null(self, client: TestClient, db_session):
        """
        description is nullable — the API must handle None without crashing.
        """
        tool = Tool(id="nodesc", name="No Description Tool", category="Testing", description=None)
        db_session.add(tool)
        db_session.commit()

        response = client.get("/tools/nodesc")

        assert response.status_code == 200
        assert response.json()["description"] is None