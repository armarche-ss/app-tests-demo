# =============================================================================
# Makefile — Demo commands
#
# Uses `docker compose` (v2 CLI plugin) — NOT the old `docker-compose`.
# Run `docker compose version` to verify you have the v2 plugin.
#
# Usage: make <target>
# =============================================================================

.PHONY: help up down logs status restart \
        test-unit test-integration test-smoke test-perf test-all \
        patch-break patch-fix-unit patch-fix-integration \
        patch-fix-smoke patch-fix-perf patch-reset

# Default: show help
help:
	@echo ""
	@echo "  DevOps Tools Rating — Demo Commands"
	@echo "  ════════════════════════════════════"
	@echo ""
	@echo "  INFRASTRUCTURE"
	@echo "    make up              Build and start all services"
	@echo "    make down            Stop all services (keep DB data)"
	@echo "    make down-clean      Stop all services and wipe DB data"
	@echo "    make restart         Restart API after a code change"
	@echo "    make logs            Tail API logs"
	@echo "    make status          Show running containers"
	@echo ""
	@echo "  TESTING"
	@echo "    make test-unit           Run unit tests locally (no Docker)"
	@echo "    make test-integration    Run integration tests in Docker"
	@echo "    make test-smoke          Run smoke tests in Docker"
	@echo "    make test-perf           Run Locust load test (headless, 30s)"
	@echo "    make test-all            Run all test stages in sequence"
	@echo ""
	@echo "  PATCHES (teaching demo)"
	@echo "    make patch-break         Introduce all 4 bugs"
	@echo "    make patch-fix-unit      Fix Bug 1 (unit tests go green)"
	@echo "    make patch-fix-integration Fix Bug 2 (integration go green)"
	@echo "    make patch-fix-smoke     Fix Bug 3 (smoke tests go green)"
	@echo "    make patch-fix-perf      Fix Bug 4 (performance goes green)"
	@echo "    make patch-reset         Revert everything to the original"
	@echo ""
	@echo "  Access:"
	@echo "    UI:   http://localhost"
	@echo "    Docs: http://localhost/api/docs"
	@echo ""

# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------

up:
	@echo "🚀 Building and starting services..."
	docker compose up -d --build
	@echo ""
	@echo "  ✅ Stack is up"
	@echo "  UI:   http://localhost"
	@echo "  Docs: http://localhost/api/docs"
	@echo ""

down:
	docker compose down

down-clean:
	docker compose down -v

restart:
	@echo "🔄 Restarting API service..."
	docker compose restart api
	@echo "✅ API restarted"

logs:
	docker compose logs -f api

status:
	docker compose ps

# ---------------------------------------------------------------------------
# Unit tests — run locally, zero Docker dependency
# ---------------------------------------------------------------------------

install-deps:
	pip install -r requirements-test.txt

test-unit:
	@echo ""
	@echo "════════════════════════════════════════════"
	@echo "  🧪 UNIT TESTS"
	@echo "  Runs locally. No Docker, no DB required."
	@echo "════════════════════════════════════════════"
	pytest tests/unit/ -v --tb=short
	@echo ""

# ---------------------------------------------------------------------------
# Integration tests — run inside the tests container (real PostgreSQL)
# ---------------------------------------------------------------------------

test-integration:
	@echo ""
	@echo "════════════════════════════════════════════"
	@echo "  🔗 INTEGRATION TESTS"
	@echo "  Runs in Docker against real PostgreSQL."
	@echo "  Requires: make up"
	@echo "════════════════════════════════════════════"
	pytest tests/integration/ -v --tb=short
	@echo ""

# ---------------------------------------------------------------------------
# Smoke tests — run inside the tests container against the live api service
# ---------------------------------------------------------------------------

test-smoke:
	@echo ""
	@echo "════════════════════════════════════════════"
	@echo "  💨 SMOKE TESTS"
	@echo "  Hits the live API container over Docker network."
	@echo "  Requires: make up"
	@echo "════════════════════════════════════════════"
	SMOKE_BASE_URL=http://localhost:8000 pytest tests/smoke/ -v --tb=short
# 	docker compose run --rm --profile testing tests \
# 	  pytest tests/smoke/ -v --tb=short
	@echo ""

# ---------------------------------------------------------------------------
# Performance tests — Locust headless run (30 seconds, 50 users)
# ---------------------------------------------------------------------------

test-perf:
	@echo ""
	@echo "════════════════════════════════════════════"
	@echo "  ⚡ PERFORMANCE TESTS (Locust, 30s, 50 users)"
	@echo "  Requires: make up"
	@echo "════════════════════════════════════════════"
	docker compose --profile testing run --rm tests \
	  locust \
	    -f tests/performance/locustfile.py \
	    --host http://api:8000 \
	    --headless \
	    -u 50 -r 5 \
	    --run-time 30s
	@echo ""

# Run all test stages in sequence
test-all: test-unit test-integration test-smoke test-perf
	@echo "✅ All test stages complete."

# ---------------------------------------------------------------------------
# Patches — the teaching demo
# ---------------------------------------------------------------------------

patch-break:
	@echo ""
	@echo "💥 Introducing the breaking change..."
	@echo "   4 bugs hidden in this patch — can you spot them?"
	@echo ""
	git apply patches/00_breaking.patch
	@echo ""
	@echo "✅ Patch applied."
	@echo "   Next: make test-unit"
	@echo ""

patch-fix-unit:
	@echo ""
	@echo "🔧 Fix 1/4 — restoring correct score validation..."
	git apply patches/01_fix_unit.patch
	@echo "✅ Fixed. Run: make test-unit"
	@echo ""

patch-fix-integration:
	@echo ""
	@echo "🔧 Fix 2/4 — restoring DB_PORT env var name..."
	git apply patches/02_fix_integration.patch
	@echo "✅ Fixed. Run: make restart && make test-integration"
	@echo ""

patch-fix-smoke:
	@echo ""
	@echo "🔧 Fix 3/4 — restoring /health endpoint..."
	git apply patches/03_fix_smoke.patch
	@echo "✅ Fixed. Run: make restart && make test-smoke"
	@echo ""

patch-fix-perf:
	@echo ""
	@echo "🔧 Fix 4/4 — restoring DB index on ratings.tool_id..."
	git apply patches/04_fix_perf.patch
	@echo "✅ Fixed. Run: make restart && make test-perf"
	@echo ""
	@echo "🎉 All 4 bugs fixed. All test stages should now be green."
	@echo ""

patch-reset:
	@echo "⏪ Reverting all patches to original state..."
	git checkout app/
	@echo "✅ Restored. Run: make restart"
