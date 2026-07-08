"""
Live GitHub star synchronisation.

This module holds the work that runs *after* the HTTP response is sent — the
FastAPI background task scheduled by ``POST /tools/sync``. It reaches out to the
GitHub REST API for each tool's repository, reads the current star count, and
writes it (plus a ``last_synced_at`` timestamp) back into the database.

Teaching note: a background task runs *after* the request finishes, so the
request-scoped session from ``get_db`` is already closed by the time this code
runs. That is why ``sync_all_tool_stars`` opens its **own** ``SessionLocal``.
"""

import os
import logging
from datetime import datetime, timezone

import httpx

from app.database import SessionLocal
from app.models import Tool

logger = logging.getLogger(__name__)

# Overridable so tests / other environments can point elsewhere; the default is
# the real public GitHub API.
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")

# GitHub requires a User-Agent. An optional token raises the unauthenticated
# rate limit (60 req/hour) to 5000 req/hour.
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def _headers() -> dict:
    headers = {
        "User-Agent": "devops-tools-rating-api",
        "Accept": "application/vnd.github+json",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def fetch_repo_stars(client: httpx.Client, repo: str) -> int | None:
    """
    Return the current star count for ``owner/name``, or ``None`` on any error.

    Errors are swallowed (and logged) on purpose: one unreachable or renamed
    repository should not abort the whole sync.
    """
    try:
        resp = client.get(f"{GITHUB_API_URL}/repos/{repo}", headers=_headers())
        resp.raise_for_status()
        return int(resp.json()["stargazers_count"])
    except Exception as exc:  # noqa: BLE001 — best-effort per-repo fetch
        logger.warning("Failed to fetch stars for %s: %s", repo, exc)
        return None


def sync_all_tool_stars() -> None:
    """
    Background task: refresh every tool's star count from GitHub.

    Opens its own database session (see module docstring), fetches stars for
    each tool that has a ``github_repo``, and — on success — records both the new
    count and the moment it was synced.
    """
    db = SessionLocal()
    try:
        with httpx.Client(timeout=10.0) as client:
            tools = db.query(Tool).filter(Tool.github_repo.isnot(None)).all()
            for tool in tools:
                stars = fetch_repo_stars(client, tool.github_repo)
                if stars is None:
                    continue
                tool.github_stars = stars
                tool.last_synced_at = datetime.now(timezone.utc)
        db.commit()
        logger.info("Star sync complete for %d tools", len(tools))
    finally:
        db.close()
