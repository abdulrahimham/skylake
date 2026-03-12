.PHONY: help setup install up down restart logs \
        lint typecheck test \
        dbt-compile dbt-run dbt-test dbt-docs \
        ingest soda ci clean

help:
	@echo ""
	@echo "SkyLake — Available Commands"
	@echo "────────────────────────────"
	@echo "  make setup        Install deps + copy .env"
	@echo "  make up           Start all Docker services"
	@echo "  make down         Stop all Docker services"
	@echo "  make lint         Run ruff linter"
	@echo "  make test         Run unit tests"
	@echo "  make dbt-compile  Compile dbt models"
	@echo "  make dbt-test     Run dbt tests"
	@echo "  make ingest       Run manual ingestion"
	@echo "  make soda         Run Soda Core checks"
	@echo "  make ci           Run full CI suite locally"
	@echo "  make clean        Remove generated artifacts"
	@echo ""

setup:
	uv sync --extra dev
	cp -n .env.example .env || true
	@echo "✅ Environment ready. Edit .env if needed."

install:
	uv sync --extra dev

up:
	docker compose up -d
	@echo "✅ Services running"

down:
	docker compose down
	@echo "✅ Services stopped"

restart:
	docker compose restart

logs:
	docker compose logs -f

lint:
	uv run ruff check .
	@echo "✅ Lint passed"

typecheck:
	uv run mypy ingestion/ dagster/
	@echo "✅ Type check passed"

test:
	uv run pytest tests/unit/ -v
	@echo "✅ Unit tests passed"

dbt-compile:
	cd dbt/skylake_dbt && uv run dbt compile --profiles-dir .
	@echo "✅ dbt compiled"

dbt-run:
	cd dbt/skylake_dbt && uv run dbt run --profiles-dir .
	@echo "✅ dbt models built"

dbt-test:
	cd dbt/skylake_dbt && uv run dbt test --profiles-dir .
	@echo "✅ dbt tests passed"

dbt-docs:
	cd dbt/skylake_dbt && uv run dbt docs generate --profiles-dir .
	cd dbt/skylake_dbt && uv run dbt docs serve --profiles-dir .

ingest:
	uv run python -m ingestion.clients.noaa_client
	@echo "✅ Ingestion complete"

soda:
	uv run soda scan -d skylake_duckdb \
		-c soda/configuration.yml \
		soda/checks/
	@echo "✅ Soda checks complete"

ci: lint test dbt-compile
	@echo "✅ All CI checks passed — safe to push"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf dbt/skylake_dbt/target/
	rm -rf dbt/skylake_dbt/logs/
	@echo "✅ Cleaned generated artifacts"
