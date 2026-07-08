# DevOps Tools Rating API

A FastAPI-based REST API for rating and discovering open-source tools used by DevOps engineers. This project demonstrates a comprehensive testing strategy with unit, integration, smoke, and performance tests, as well as a patch-based system for teaching test-driven development concepts.

## Project Overview

The DevOps Tools Rating API provides endpoints to manage and retrieve information about DevOps tools. The application uses PostgreSQL for persistent storage and includes a complete test suite that validates functionality at multiple levels.

### Key Features

- REST API for managing DevOps tools
- PostgreSQL database integration
- Live GitHub star sync via a FastAPI background task (`POST /tools/sync`)
- Frontend with a "Sync stars" button, a "last synced" indicator, and star icons that link to each tool's GitHub page
- Health check endpoint for system monitoring
- Comprehensive test coverage (unit, integration, smoke, performance, end-to-end)
- Docker and Docker Compose support for easy deployment
- Patch-based demonstration system for testing stages

## Project Structure

```
app-tests-demo/
├── app/                          # FastAPI application code
│   ├── __init__.py
│   ├── main.py                  # FastAPI app configuration and root routes
│   ├── config.py                # Environment variables and configuration
│   ├── database.py              # Database setup and session management
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── crud.py                  # Database CRUD operations
│   ├── services.py              # GitHub star fetch + sync background task
│   └── routers/                 # FastAPI route handlers
│       ├── __init__.py
│       ├── health.py            # Health check endpoint
│       └── tools.py             # Tools API endpoints (list, get, sync)
├── tests/                       # Test suite
│   ├── conftest.py             # pytest configuration and fixtures
│   ├── unit/                   # Unit tests
│   │   └── test_services.py
│   ├── integration/            # Integration tests
│   │   └── test_tools_api.py
│   ├── smoke/                  # Smoke tests (requires running server)
│   │   └── test_smoke.py
│   ├── performance/            # Performance tests
│   │   └── locustfile.py
│   └── e2e/                    # End-to-end browser tests (Selenium)
│       ├── conftest.py
│       ├── test_star_icon.py
│       └── test_sync.py
├── patches/                    # Git patches for bug demonstrations
│   └── 00_breaking.patch      # Introduces 5 bugs
├── frontend/                   # Frontend files
│   ├── Dockerfile
│   ├── index.html
│   └── nginx.conf
├── scripts/                    # Utility scripts
│   └── init-db.sh
├── Dockerfile                  # API service Dockerfile
├── Dockerfile.tests           # Tests service Dockerfile
├── Dockerfile.e2e             # End-to-end (Selenium) test image
├── docker-compose.yml         # Docker Compose configuration
├── Makefile                   # Make targets for common tasks
├── pytest.ini                 # pytest configuration
├── pyproject.toml             # Python project metadata and dependencies
├── uv.lock                    # Locked dependency versions (uv)
└── README.md                  # This file
```

## Running the Application

### Start with Docker Compose

```bash
make up
```

This builds and starts all services:
- API server on http://localhost:8000
- PostgreSQL database
- Frontend on http://localhost:80

### Stop Services

```bash
make down
```

## Testing

The project includes five levels of testing, each designed to catch different types of bugs. The unit/integration/smoke/performance tests run inside the `tests` Docker Compose service (built from `Dockerfile.tests`); the end-to-end tests run inside the `e2e` service (built from `Dockerfile.e2e`). The `make test-*` targets build and start everything they depend on (`db`, `api`, and for e2e also `frontend`) automatically — no manual setup required.

### Unit Tests
Test individual functions in isolation without external dependencies.

```bash
make test-unit
```

Catches: Logic errors, incorrect calculations, data validation issues

### Integration Tests
Test the API endpoints with a real database, verifying the complete flow from HTTP request to database and back.

```bash
make test-integration
```

Catches: Database query errors, API response structure issues, ordering/filtering bugs

### Smoke Tests
Test the running application with HTTP requests, validating that the deployed system works end-to-end.

```bash
make test-smoke
```

Catches: Routing errors, missing endpoints, configuration issues

### Performance Tests
Load test the application to ensure acceptable response times under stress.

```bash
make test-perf
```

Catches: Performance bottlenecks, resource contention, scalability issues

### End-to-End (E2E) Tests
Drive a real browser (Selenium) against the running frontend, exercising the full stack: UI → nginx → API → database → the live GitHub API. The browser runs in a dedicated `selenium` service; the `e2e` service runs the tests and connects to it remotely.

```bash
make test-e2e
```

Catches: Broken UI wiring and — uniquely — broken **background side-effects** that are invisible to a single API response. `test_sync.py` clicks "Sync stars" and waits for the `last_synced_at` timestamp to actually advance.

> Note: `test-e2e` is intentionally **not** part of `make test-all` because it drives a real browser and calls the live GitHub API (subject to rate limits). Run it on its own.

### Run All Tests

```bash
make test-all
```

This runs the unit, integration, smoke, and performance tests in order. Run the end-to-end tests separately with `make test-e2e`.

## Patch System (Bug Demonstration)

This project includes a patch file that introduces bugs to demonstrate how different test levels catch errors.

### Available Patch Targets

```bash
# Introduce all 5 bugs at once
make patch-break

# Reset to clean state
make patch-reset
```

### Patch Details

**00_breaking.patch** - Introduces 5 bugs designed to be caught at different test levels:

1. **Unit Test Level Bug** - Incorrect database query logic in CRUD operations
2. **Integration Test Level Bug** - Tool ordering by wrong field instead of name
3. **Smoke Test Level Bug** - Missing route registration
4. **Performance Test Level Bug** - Inefficient operations causing slow responses
5. **E2E Test Level Bug** - The star-sync background task stops stamping `last_synced_at`. The API response schema and every single-request test still pass — only the end-to-end test (which clicks "Sync stars" and waits for the timestamp to change) catches it.

These bugs demonstrate how:
- Unit tests catch logic and calculation errors
- Integration tests catch database and API issues
- Smoke tests catch routing and configuration errors
- Performance tests catch performance bottlenecks
- End-to-end tests catch broken user-visible behavior and background side-effects that lower levels miss
