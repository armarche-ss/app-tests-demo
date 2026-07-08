.PHONY: up down logs status restart \
        test-unit test-integration test-smoke test-perf test-e2e test-all \
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
	uv sync --group test

test-unit: up
	docker compose --profile testing run --rm tests \
	  pytest unit/ -v --tb=short

test-integration: up
	docker compose --profile testing run --rm tests \
	  pytest integration/ -v --tb=short

test-smoke: up
	docker compose --profile testing run --rm tests \
	  pytest smoke/ -v --tb=short

test-perf: up
	docker compose --profile testing run --rm tests \
	  locust \
	    -f /tests/performance/locustfile.py \
	    --host http://api:8000 \
	    --headless \
	    -u 50 -r 5 \
	    --run-time 30s

# End-to-end (browser) tests — the top of the pyramid.
# Kept out of `test-all` because it drives a real browser and hits the live
# GitHub API (subject to rate limits).
# --build rebuilds the e2e image (it's in the `testing` profile, so `up` above
# does not build it) and starts the `selenium` browser it depends on.
test-e2e: up
	docker compose --profile testing run --build --rm e2e \
	  pytest e2e/ -v

test-all: test-unit test-integration test-smoke test-perf

patch-break:
	git apply patches/00_breaking.patch

patch-reset:
	git checkout app/
