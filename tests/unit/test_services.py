"""
tests/unit/test_services.py — Unit tests for crud.py

═══════════════════════════════════════════════════════════════════════
WHAT ARE UNIT TESTS?
═══════════════════════════════════════════════════════════════════════
Unit tests verify a single function in complete isolation.

"Isolation" means:
  ✅ No database (we use MagicMock to fake it)
  ✅ No HTTP server
  ✅ No Docker
  ✅ Extremely fast — runs in milliseconds

How mocking works:
  MagicMock() creates a fake object that records every call made on it.
  We configure it to return specific values (like a fake Tool), then
  call the real function and assert it behaved correctly.

Run with:
  pytest tests/unit/ -v
  (no Docker, no running services needed)
═══════════════════════════════════════════════════════════════════════
"""
import pytest
from unittest.mock import MagicMock

from app import crud, models


class TestGetToolById:
    """
    Unit tests for crud.get_tool_by_id().

    This function takes a db session and a tool_id string, and returns
    the matching Tool ORM object (or None if not found).
    """

    def _mock_db(self, return_value):
        """
        Helper: builds a MagicMock that returns `return_value` when
        db.query(...).filter(...).first() is called.

        This is the exact chain of calls that get_tool_by_id() makes
        internally, so the mock must match it exactly.
        """
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = return_value
        return mock_db

    def test_returns_tool_when_found(self):
        """
        Happy path: the DB returns a tool — we get it back.
        """
        fake_tool = models.Tool(
            id="grafana",
            name="Grafana",
            category="Observability",
            description="Beautiful dashboards.",
            github_stars=65000,
        )
        mock_db = self._mock_db(fake_tool)

        result = crud.get_tool_by_id(mock_db, tool_id="grafana")

        assert result is fake_tool
        assert result.name == "Grafana"
        assert result.category == "Observability"

    def test_returns_none_when_not_found(self):
        """
        When the DB has no matching row, first() returns None.
        Our function should pass that None through unchanged.
        """
        mock_db = self._mock_db(None)

        result = crud.get_tool_by_id(mock_db, tool_id="nonexistent-tool")

        assert result is None

    def test_queries_by_correct_id(self):
        """
        Verify the function actually calls query() on the db session.
        If it returned a hardcoded value, this assertion would catch it.
        """
        mock_db = self._mock_db(None)

        crud.get_tool_by_id(mock_db, tool_id="pytest")

        # Confirm that a query was actually made against the database
        mock_db.query.assert_called_once_with(models.Tool)


class TestGetAllTools:
    """
    Unit tests for crud.get_all_tools().

    This function returns every tool in the database, ordered by name.
    """

    def test_returns_all_tools(self):
        """
        The function should return whatever the DB query returns.
        """
        fake_tools = [
            models.Tool(id="ansible", name="Ansible", category="IaC",    github_stars=63200),
            models.Tool(id="docker",  name="Docker",  category="Containers", github_stars=69000),
        ]
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = fake_tools

        result = crud.get_all_tools(mock_db)

        assert result == fake_tools
        assert len(result) == 2

    def test_returns_empty_list_when_no_tools(self):
        """
        If the tools table is empty, we get an empty list — not an error.
        """
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = []

        result = crud.get_all_tools(mock_db)

        assert result == []

    def test_calls_database(self):
        """
        Sanity check: get_all_tools() must actually query the database.
        """
        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = []

        crud.get_all_tools(mock_db)

        mock_db.query.assert_called_once_with(models.Tool)
