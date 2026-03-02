# DevOps Tools Rating API

A FastAPI-based REST API for rating and discovering open-source tools used by DevOps engineers. This project demonstrates a comprehensive testing strategy with unit, integration, smoke, and performance tests, as well as a patch-based system for teaching test-driven development concepts.

## Project Overview

The DevOps Tools Rating API provides endpoints to manage and retrieve information about DevOps tools. The application uses PostgreSQL for persistent storage and includes a complete test suite that validates functionality at multiple levels.

### Key Features

- REST API for managing DevOps tools
- PostgreSQL database integration
- Health check endpoint for system monitoring
- Comprehensive test coverage (unit, integration, smoke, performance)
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
│   └── routers/                 # FastAPI route handlers
│       ├── __init__.py
│       ├── health.py            # Health check endpoint
│       └── tools.py             # Tools API endpoints
├── tests/                       # Test suite
│   ├── conftest.py             # pytest configuration and fixtures
│   ├── unit/                   # Unit tests
│   │   └── test_services.py
│   ├── integration/            # Integration tests
│   │   └── test_tools_api.py
│   ├── smoke/                  # Smoke tests (requires running server)
│   │   └── test_smoke.py
│   └── performance/            # Performance tests
│       └── locustfile.py
├── patches/                    # Git patches for bug demonstrations
│   └── 00_breaking.patch      # Introduces 4 bugs
├── frontend/                   # Frontend files
│   ├── Dockerfile
│   ├── index.html
│   └── nginx.conf
├── scripts/                    # Utility scripts
│   └── init-db.sh
├── Dockerfile                  # API service Dockerfile
├── Dockerfile.tests           # Tests service Dockerfile
├── docker-compose.yml         # Docker Compose configuration
├── Makefile                   # Make targets for common tasks
├── pytest.ini                 # pytest configuration
├── requirements.txt           # Python production dependencies
├── requirements-test.txt      # Python testing dependencies
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

The project includes four levels of testing, each designed to catch different types of bugs:

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

Requires: API server running on http://localhost:8000

Catches: Routing errors, missing endpoints, configuration issues

### Performance Tests
Load test the application to ensure acceptable response times under stress.

```bash
make test-perf
```

Requires: Docker Compose stack running

Catches: Performance bottlenecks, resource contention, scalability issues

### Run All Tests

```bash
make test-all
```

This runs the complete test suite in order: unit, integration, smoke, and performance tests.

## Patch System (Bug Demonstration)

This project includes a patch file that introduces bugs to demonstrate how different test levels catch errors.

### Available Patch Targets

```bash
# Introduce all 4 bugs at once
make patch-break

# Reset to clean state
make patch-reset
```

### Patch Details

**00_breaking.patch** - Introduces 4 bugs designed to be caught at different test levels:

1. **Unit Test Level Bug** - Incorrect database query logic in CRUD operations
2. **Integration Test Level Bug** - Tool ordering by wrong field instead of name
3. **Smoke Test Level Bug** - Missing route registration
4. **Performance Test Level Bug** - Inefficient operations causing slow responses

These bugs demonstrate how:
- Unit tests catch logic and calculation errors
- Integration tests catch database and API issues
- Smoke tests catch routing and configuration errors
- Performance tests catch performance bottlenecks
