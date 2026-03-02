.PHONY: up down logs status restart \
        test-unit test-integration test-smoke test-perf test-all \
        patch-break patch-fix-unit patch-fix-integration \
        patch-fix-smoke patch-fix-perf patch-reset


build:
	docker compose build --no-cache

up: build
	docker compose up -d --build

down:
	docker compose down

down-clean:
	docker compose down -v



install-deps:
	pip install -r requirements-test.txt

test-unit: install-deps
	pytest tests/unit/ -v --tb=short

test-integration:
	pytest tests/integration/ -v --tb=short

test-smoke:
	SMOKE_BASE_URL=http://localhost:8000 pytest tests/smoke/ -v --tb=short

test-perf:
	docker compose --profile testing run --rm tests \
	  locust \
	    -f /tests/performance/locustfile.py \
	    --host http://api:8000 \
	    --headless \
	    -u 50 -r 5 \
	    --run-time 30s

test-all: test-unit test-integration test-smoke test-perf

patch-break:
	git apply patches/00_breaking.patch

patch-reset:
	git checkout app/
