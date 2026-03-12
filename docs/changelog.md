# Changelog

All notable changes to SkyLake are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### In Progress
- Phase 1: NOAA API ingestion client
- Phase 1: METAR and TAF parsers
- Phase 1: Raw layer writer with date partitioning
- Phase 1: First Dagster asset definitions

---

## [0.1.0] - 2026-03-12

Phase 0 — Foundation complete.

### Added
- Full project folder structure for all pipeline layers
- pyproject.toml with complete dependency list managed by uv
- Makefile with developer workflow commands
  (setup, lint, test, dbt-compile, dbt-test, ingest, soda, ci)
- Root README with architecture overview and quickstart
- GitHub Actions CI pipeline running lint and unit tests on push
- Docker Compose with Dagster and Streamlit services
- Dagster Dockerfile
- Streamlit Dockerfile and app placeholder
- docs/architecture.md — full system architecture overview
- docs/roadmap.md — MVP scope and production upgrade path
- docs/data_model.md — layer-by-layer data model documentation
- docs/data_dictionary.md — field-level definitions (in progress)
- docs/ingestion_runbook.md — operational runbook (in progress)
- docs/demo_notes.md — presentation notes (in progress)
- ADR-001: Storage format — DuckDB + Parquet
- ADR-002: Orchestration — Dagster over Airflow
- ADR-003: Transformation — dbt-core
- ADR-004: Data quality — Soda Core + dbt tests
- ADR-005: API source — NOAA Aviation Weather Center

### Technical Decisions
- Python 3.11 as minimum runtime version
- uv for dependency management over pip or Poetry
- Dagster over Apache Airflow for orchestration
- dbt-core + dbt-duckdb for transformation
- DuckDB + Parquet for MVP storage layer
- Soda Core for bronze layer data quality
- Docker + Compose for full reproducibility
- GitHub Actions for CI on every push

---

## Version Guide

| Version | Milestone |
|---|---|
| 0.1.0 | Phase 0 complete — foundation and documentation |
| 0.2.0 | Phase 1 complete — raw ingestion working |
| 0.3.0 | Phase 2 complete — bronze layer and Soda checks |
| 0.4.0 | Phase 3 complete — silver layer dbt models |
| 0.5.0 | Phase 4 complete — gold layer data products |
| 0.6.0 | Phase 5 complete — full Dagster orchestration |
| 0.7.0 | Phase 6 complete — data quality integrated |
| 0.8.0 | Phase 7 complete — Streamlit dashboard |
| 0.9.0 | Phase 8 complete — CI and Docker production-ready |
| 1.0.0 | Phase 9 complete — fully documented, demo-ready |
