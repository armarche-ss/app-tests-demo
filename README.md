# 🧪 Testing Stages — DevOps Tools Rating API

> **A hands-on demo for teaching unit, integration, smoke, and performance testing.**
> FastAPI backend + PostgreSQL + nginx frontend, all running via Docker Compose.

---

## 📐 Project Structure

```
devops-rating-api/
├── app/
│   ├── main.py           ← FastAPI entry point + seed data
│   ├── database.py       ← DB connection (reads env vars)
│   ├── models.py         ← SQLAlchemy table definitions
│   ├── schemas.py        ← Pydantic request/response shapes
│   ├── services.py       ← Business logic (primary unit test target)
│   └── routers/
│       ├── tools.py      ← HTTP endpoints for tools + ratings
│       └── health.py     ← GET /health endpoint
│
├── frontend/
│   ├── index.html        ← Full UI (vanilla JS, no build step)
│   ├── nginx.conf        ← Serves UI + proxies /api/* → api:8000
│   └── Dockerfile        ← nginx container
│
├── tests/
│   ├── conftest.py       ← Fixtures: SQLite locally, PostgreSQL in Docker
│   ├── unit/             ← Pure logic tests, no DB, no Docker
│   ├── integration/      ← Real DB, full HTTP flow
│   ├── smoke/            ← Live server health checks
│   └── performance/      ← Locust load tests
│
├── patches/
│   ├── 00_breaking.patch         ← Introduces 4 bugs at once
│   ├── 01_fix_unit.patch         ← Fixes Bug 1
│   ├── 02_fix_integration.patch  ← Fixes Bug 2
│   ├── 03_fix_smoke.patch        ← Fixes Bug 3
│   └── 04_fix_perf.patch         ← Fixes Bug 4
│
├── Dockerfile            ← API container
├── Dockerfile.tests      ← Test runner container (integration/smoke/perf)
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────┐
                    │         Docker Network          │
                    │                                 │
Browser             │  ┌──────────┐   ┌────────────┐ │
   │                │  │ frontend │   │    api     │ │
   └──[port 80]────►│  │  nginx   ├──►│  FastAPI   │ │
                    │  │          │   │ :8000      │ │
                    │  └──────────┘   └─────┬──────┘ │
                    │                       │        │
                    │                  ┌────▼──────┐ │
                    │                  │    db     │ │
                    │                  │ PostgreSQL│ │
                    │                  │ :5432     │ │
                    │                  └───────────┘ │
                    └─────────────────────────────────┘

Port policy:
  ✅ frontend:80  → published  (users access the app here)
  ❌ api:8000     → internal only  (nginx proxies to it)
  ❌ db:5432      → internal only  (only api talks to it)
```

**nginx proxy rules:**
- `GET /`       → serves `index.html`
- `GET /api/*`  → proxied to `http://api:8000/*`

---

## ⚙️ Prerequisites

```bash
docker compose version   # must be v2 (comes with Docker Desktop)
python3 --version        # 3.11+
git --version
```

---

## 🚀 Part 1 — Start the App

### Step 1.1 — Initialize git (required for patches)

```bash
cd devops-rating-api
git init
git add .
git commit -m "initial: working app with full test suite"
```

### Step 1.2 — Install test dependencies locally (for unit tests)

```bash
pip install -r requirements-test.txt
```

### Step 1.3 — Start the stack

```bash
make up
```

Open in browser:
- **UI:** http://localhost
- **API docs:** http://localhost/api/docs

👉 **Walk through the UI** — show filtering, star ratings, the API health indicator in the footer.
👉 **Walk through /api/docs** — show the endpoints: list tools, rate a tool, get rating summary.

---

## 🧪 Part 2 — The Testing Pyramid

```
              /\
             /  \   Smoke + Performance
            /    \  (few, slow, needs live server)
           /──────\
          /        \ Integration
         /          \ (moderate, needs DB)
        /────────────\
       /              \ Unit tests
      /                \ (many, fast, fully isolated)
     /──────────────────\
```

---

## 🔬 Part 3 — Unit Tests

**What:** Tests `validate_rating_score()` and the service layer using mocks.
**How:** Pure Python — `unittest.mock.MagicMock` fakes the database.
**Where:** Runs locally. No Docker. No DB.

```bash
make test-unit
```

Expected output — all green. Completes in < 1 second.

💡 **Key point:** A unit test that runs in 2ms is free to run thousands of times in CI.
   These tests are the safety net you commit with every change.

---

## 🔗 Part 4 — Integration Tests

**What:** Full HTTP request → router → service → real database → response.
**How:** Runs inside the `tests` container, connected to real PostgreSQL.
**Where:** Inside Docker (shares the app network).

```bash
make test-integration
```

💡 **Key point:** Integration tests exercise the database layer — SQL queries,
   foreign keys, schema mismatches. Unit tests with mocks can't see any of this.

---

## 💨 Part 5 — Smoke Tests

**What:** HTTP requests to the live running API (`http://api:8000`).
**How:** `requests` library hitting the real server. No mocks.
**Where:** Inside Docker (same network as the api container).

```bash
make test-smoke
```

💡 **Key point:** Smoke tests answer "is it alive?" after a deployment.
   They catch things like: wrong port binding, crash on startup, missing routes,
   environment variables not set.

---

## ⚡ Part 6 — Performance Tests

**What:** 50 virtual users hammering the API simultaneously for 30 seconds.
**How:** Locust — Python-based load testing.
**Where:** Inside Docker.

```bash
make test-perf
```

💡 **Key point:** A smoke test with 1 user on 10 rows is fast no matter what.
   Locust with 50 concurrent users against thousands of rows reveals real bottlenecks
   — like a missing database index.

---

## 💥 Part 7 — The Breaking Change

```bash
make patch-break
```

👉 **Ask the class:** look at the diff below. Can you spot all 4 bugs?

| # | File | Bug | Caught by |
|---|------|-----|-----------|
| 1 | `services.py`  | `1 <= score` → `0 <= score` (score=0 now valid) | **Unit tests** |
| 2 | `database.py`  | reads `DATABASE_PORT` instead of `DB_PORT` | **Integration tests** |
| 3 | `health.py`    | entire `/health` endpoint deleted | **Smoke tests** |
| 4 | `models.py`    | `Index("ix_ratings_tool_id")` removed | **Performance tests** |

---

## 🔧 Part 8 — Fix Bugs One at a Time

### Bug 1 — Unit Tests catch it

```bash
make test-unit
# FAILED: test_score_0_is_invalid — validate_rating_score(0) returned True!

make patch-fix-unit
make test-unit       # ✅ green
```

💬 The unit test called `validate_rating_score(0)`, expected `False`, got `True`.
   One line. Caught in milliseconds without Docker.

---

### Bug 2 — Integration Tests catch it

```bash
make test-integration
# FAILED: test_health_check_returns_200
# OperationalError: could not connect to server

make patch-fix-integration
make restart
make test-integration   # ✅ green
```

💬 The integration test used a **real database connection** — so it felt the wrong env var name.
   Unit tests mock the DB completely; they never called `create_engine()`.
   This is exactly why we need both layers.

---

### Bug 3 — Smoke Tests catch it

```bash
make test-smoke
# FAILED: test_health_endpoint_returns_ok
# AssertionError: /health returned 404

make patch-fix-smoke
make restart
make test-smoke         # ✅ green
```

💬 Unit and integration tests test individual functions and DB calls.
   Neither checks "was the route actually registered in the running server?"
   Only smoke tests do — because they hit the real server.

---

### Bug 4 — Performance Tests catch it

```bash
make test-perf
# GET /tools/{id}/rating — avg response time > 500ms → THRESHOLD EXCEEDED

make patch-fix-perf
make restart
make test-perf          # ✅ response times normalize
```

💬 The rating endpoint runs `SELECT AVG(score) FROM ratings WHERE tool_id = ?`.
   Without an index, PostgreSQL scans the entire table for every request.
   With 1 user: fast. With 50 concurrent users and thousands of rows: disaster.
   Smoke tests never reveal this — they use 1 user on a nearly empty DB.

---

## ✅ Final State

```bash
make test-unit           # ✅
make test-integration    # ✅
make test-smoke          # ✅
make test-perf           # ✅
```

---

## 🔑 Key Takeaways

| Stage | Runs against | Speed | Catches |
|-------|-------------|-------|---------|
| **Unit** | Mocks | ⚡ <1s | Logic bugs, off-by-one |
| **Integration** | Real DB in Docker | 🏃 ~5s | SQL errors, env config, HTTP contract |
| **Smoke** | Live server in Docker | 🚶 ~10s | Deployment failures, missing routes |
| **Performance** | Live server + load | 🐢 ~1min | DB bottlenecks, concurrency issues |

---

## 🔁 Reset

```bash
make patch-reset    # revert code
make restart        # restart API with clean code
```

Or full wipe:
```bash
make down-clean     # stops everything and deletes DB volume
make up             # fresh start
```
