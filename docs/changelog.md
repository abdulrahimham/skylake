# Changelog

All notable changes to SkyLake are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### In Progress
- Phase 2: dbt project initialization and bronze layer models
- Phase 2: DuckDB connection and Parquet writer
- Phase 2: Soda Core checks for bronze layer

---

## [0.2.0] - 2026-03-13

Phase 1 — Raw Ingestion complete.

### Added
- ingestion/clients/base_client.py — reusable HTTP client with timeout and error handling
- ingestion/clients/noaa_client.py — NOAA AWC API client for METARs and TAFs
- ingestion/writers/raw_writer.py — date-partitioned raw JSON writer with lineage metadata
- ingestion/utils/logging.py — consistent log formatting across ingestion layer
- ingestion/ingest.py — main ingestion script wiring client and writer together
- pipeline/skylake/resources/noaa_resource.py — Dagster ConfigurableResource for NOAA client
- pipeline/skylake/assets/raw_assets.py — raw_metar and raw_taf Dagster asset definitions
- pipeline/skylake/schedules/schedules.py — hourly_raw_ingestion_schedule (cron: 0 * * * *)
- pipeline/skylake/__init__.py — Dagster Definitions wiring assets, jobs, schedules, resources
- workspace.yaml — Dagster workspace configuration
- tests/unit/test_base_client.py — 7 unit tests for HTTP client
- tests/unit/test_noaa_client.py — 15 unit tests for NOAA client and env var handling
- tests/unit/test_raw_writer.py — 14 unit tests for file writing, partitioning, and metadata
- Fixed .python-version to pin Python 3.11

### Technical Notes
- Renamed pipeline folder from dagster/ to pipeline/ to avoid namespace collision with installed package
- 33 unit tests passing, 0 failures, 0.10s runtime
- First successful ingestion: 18 METARs + 8 TAFs in 1.1 seconds
- Raw files stored at data/raw/{metar,taf}/YYYY/MM/DD/

---

## [0.1.0] - 2026-03-12

Phase 0 — Foundation complete.

### Added
- Full project folder structure for all pipeline layers
- pyproject.toml with complete dependency list managed by uv
- Makefile with developer workflow commands
- Root README with architecture overview and quickstart
- GitHub Actions CI pipeline — lint and unit tests on every push
- Docker Compose with Dagster and Streamlit services
- Dagster Dockerfile and Streamlit Dockerfile and app placeholder
- docs/architecture.md — full system architecture with data flow diagram
- docs/data_model.md — column definitions for all 12 pipeline tables
- docs/roadmap.md — MVP scope and three-phase upgrade path
- docs/changelog.md — version history following Keep a Changelog format
- ADR-001 through ADR-005 — Architecture Decision Records

---

## Version Guide

| Version | Milestone |
|---|---|
| 0.1.0 | Phase 0 complete — foundation and documentation ✅ |
| 0.2.0 | Phase 1 complete — raw ingestion working ✅ |
| 0.3.0 | Phase 2 complete — bronze layer and Soda checks |
| 0.4.0 | Phase 3 complete — silver layer dbt models |
| 0.5.0 | Phase 4 complete — gold layer data products |
| 0.6.0 | Phase 5 complete — full Dagster orchestration |
| 0.7.0 | Phase 6 complete — data quality integrated |
| 0.8.0 | Phase 7 complete — Streamlit dashboard |
| 0.9.0 | Phase 8 complete — CI and Docker production-ready |
| 1.0.0 | Phase 9 complete — fully documented, demo-ready |
