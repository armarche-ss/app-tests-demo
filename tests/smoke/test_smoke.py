import os
import pytest
import requests

BASE_URL = os.getenv("SMOKE_BASE_URL", "http://api:8000")


@pytest.fixture(scope="session", autouse=True)
def app_is_reachable():
    """
    Checks connectivity before running any smoke test.
    If the server is not reachable, all tests are skipped with a clear message
    instead of failing with a confusing ConnectionRefusedError.

    autouse=True — runs automatically for every test in this module.
    scope="session" — only runs once for the whole test session.
    """
    try:
        requests.get(f"{BASE_URL}/", timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.skip(
            f"App is not reachable at {BASE_URL}. "
            "Start the stack first: docker compose up -d"
        )


# =============================================================================
# Smoke Tests
# =============================================================================

class TestCriticalEndpointsAlive:
    """
    Verifies that every critical endpoint returns a non-error HTTP status.
    We do NOT validate response content in detail — that is integration's job.
    Smoke tests only care: "does it respond at all?"
    """

    def test_root_is_alive(self):
        """
        GET / returns 200 — proves the app started and is routing requests.
        If this fails, the entire application is down.
        """
        response = requests.get(f"{BASE_URL}/", timeout=5)

        assert response.status_code == 200, (
            f"Root endpoint returned {response.status_code}. "
            "The application may not have started correctly."
        )

    def test_health_endpoint_exists(self):
        """
        GET /health returns 200.

        This is the most important smoke test because it verifies both:
          1. The API server is running and routing requests
          2. The database connection is working

        If this returns 404 → the /health route was removed from the code.
        If this returns 500 → the app crashed.
        If the DB is down → status will be "error" (caught by next test).
        """
        response = requests.get(f"{BASE_URL}/health", timeout=5)

        assert response.status_code == 200, (
            f"/health returned HTTP {response.status_code}. "
            "If 404: the health endpoint was removed. "
            "If 500: the application crashed."
        )

    def test_health_reports_ok(self):
        """
        The health endpoint must report status=ok and database=connected.
        A 200 with status=error means the app is up but the DB is unreachable.
        """
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()

        assert data.get("status") == "ok", (
            f"/health returned status='{data.get('status')}'. "
            f"Full response: {data}"
        )
        assert data.get("database") == "connected", (
            f"Database status: {data.get('database')}. "
            "Check DB_HOST and DB_PORT in docker-compose.yml."
        )

    def test_tools_list_endpoint_exists(self):
        """
        GET /tools/ returns 200 — the primary feature of the app is reachable.
        """
        response = requests.get(f"{BASE_URL}/tools/", timeout=5)

        assert response.status_code == 200, (
            f"/tools/ returned {response.status_code}"
        )

    def test_tools_response_is_a_list(self):
        """
        The tools endpoint must return a JSON array.
        If the DB connection failed silently, we might get a dict with an error.
        """
        response = requests.get(f"{BASE_URL}/tools/", timeout=5)
        data = response.json()

        assert isinstance(data, list), (
            f"Expected a JSON array from /tools/, got: {type(data).__name__}"
        )

    def test_api_docs_are_accessible(self):
        """
        FastAPI auto-generates interactive docs at /docs.
        If the app is misconfigured (e.g., wrong Python path), docs return 500.
        """
        response = requests.get(f"{BASE_URL}/docs", timeout=5)

        assert response.status_code == 200, (
            f"/docs returned {response.status_code}. "
            "FastAPI may not have initialized correctly."
        )

    def test_unknown_route_returns_404(self):
        """
        A request to a non-existent route should return 404, not 500.
        A 500 here would mean an unhandled exception in the global request handler.
        """
        response = requests.get(f"{BASE_URL}/this-route-does-not-exist", timeout=5)

        assert response.status_code == 404
