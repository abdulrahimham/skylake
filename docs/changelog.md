# Changelog

All notable changes to SkyLake are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### In Progress
- Phase 3: silver_metar_parsed dbt model
- Phase 3: silver_taf_parsed dbt model
- Phase 3: silver_forecast_actuals join model

---

## [0.3.0] - 2026-03-13

Phase 2 — Bronze Layer complete.

### Added
- dbt/skylake_dbt/dbt_project.yml — dbt project config with bronze/silver/gold schema layout
- ~/.dbt/profiles.yml — DuckDB connection configuration
- dbt/skylake_dbt/seeds/airport_metadata.csv — 8-airport reference table
- dbt/skylake_dbt/models/bronze/bronze_metar.sql — raw METAR JSON to typed DuckDB table
- dbt/skylake_dbt/models/bronze/bronze_taf.sql — raw TAF JSON to typed DuckDB table
- dbt/skylake_dbt/models/bronze/schema.yml — 9 dbt data quality tests
- pipeline/skylake/assets/bronze_assets.py — dagster-dbt integration for bronze models
- Updated pipeline/skylake/__init__.py — DbtCliResource and dbt assets registered

### Fixed
- SQL block comment syntax incompatible with DuckDB parser — replaced with line comments
- Visibility '10+' special value handling using TRY_CAST
- Variable wind direction 'VRB' handling in TAF bronze model

### Technical Notes
- dbt run: PASS=2, ERROR=0
- dbt test: PASS=9, ERROR=0, 0.11s runtime
- All 5 assets visible in Dagster asset lineage graph
- Bronze tables queryable at main_bronze.bronze_metar and main_bronze.bronze_taf

---

## [0.2.0] - 2026-03-13

Phase 1 — Raw Ingestion complete.

### Added
- ingestion/clients/base_client.py — reusable HTTP client
- ingestion/clients/noaa_client.py — NOAA AWC API client
- ingestion/writers/raw_writer.py — date-partitioned raw JSON writer
- ingestion/utils/logging.py — consistent log formatting
- ingestion/ingest.py — main ingestion orchestration script
- pipeline/skylake/resources/noaa_resource.py — Dagster ConfigurableResource
- pipeline/skylake/assets/raw_assets.py — raw_metar and raw_taf Dagster assets
- pipeline/skylake/schedules/schedules.py — hourly_raw_ingestion_schedule
- workspace.yaml — Dagster workspace configuration
- 33 unit tests — all passing, 0.10s runtime

---

## [0.1.0] - 2026-03-12

Phase 0 — Foundation complete.

### Added
- Full project folder structure for all pipeline layers
- pyproject.toml with complete dependency list managed by uv
- Makefile, README, GitHub Actions CI, Docker Compose
- docs/architecture.md, data_model.md, roadmap.md, changelog.md
- ADR-001 through ADR-005

---

## Version Guide

| Version | Milestone |
|---|---|
| 0.1.0 | Phase 0 complete — foundation and documentation ✅ |
| 0.2.0 | Phase 1 complete — raw ingestion working ✅ |
| 0.3.0 | Phase 2 complete — bronze layer and dbt models ✅ |
| 0.4.0 | Phase 3 complete — silver layer dbt models |
| 0.5.0 | Phase 4 complete — gold layer data products |
| 0.6.0 | Phase 5 complete — full Dagster orchestration |
| 0.7.0 | Phase 6 complete — data quality integrated |
| 0.8.0 | Phase 7 complete — Streamlit dashboard |
| 0.9.0 | Phase 8 complete — CI and Docker production-ready |
| 1.0.0 | Phase 9 complete — fully documented, demo-ready |
