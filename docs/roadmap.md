# SkyLake — Roadmap

This document outlines the current state of SkyLake,
planned improvements, and long-term production upgrade goals.

---

## Current State — MVP

The MVP covers Phase 0 through Phase 4:

- Phase 0 — Foundation: repo structure, documentation, CI, Docker
- Phase 1 — Raw Ingestion: NOAA API client, METAR + TAF ingestion
- Phase 2 — Bronze Layer: structured Parquet, Soda Core checks
- Phase 3 — Silver Layer: dbt cleaning, enrichment, METAR/TAF join
- Phase 4 — Gold Layer: risk scores, forecast accuracy, event detection

MVP delivers a fully working end-to-end pipeline on a single
laptop with no cloud infrastructure required.

---

## Near Term — Post MVP

These improvements are planned after the core pipeline is complete:

### Expand Airport Coverage
- Add 20+ additional U.S. airports
- Add international airports (EGLL London, RJTT Tokyo, YSSY Sydney)
- Group airports by region for regional analysis

### Historical Backfill
- Script to ingest 90 days of historical METAR and TAF data
- Enables trend analysis and seasonal pattern detection
- Backfill job already scaffolded at scripts/backfill.py

### Enhanced Data Products
- Runway-specific wind analysis (crosswind components)
- Departure delay risk predictor
- Airport comparison dashboard
- Weather pattern clustering by season

### Testing Improvements
- Integration tests covering full pipeline runs
- Fixtures with real NOAA API response samples
- dbt test coverage report

---

## Long Term — Production Upgrade

These upgrades move SkyLake from a local MVP to a
production-grade distributed system.

### Storage Upgrade — MinIO + Apache Iceberg
Replace local data/ directory with MinIO (S3-compatible
object store). Layer Apache Iceberg table format for:
- ACID transactions
- Time travel queries
- Schema evolution without data migration
- Partition evolution

Note: Parquet files do not change. Only the storage
location and table format layer are upgraded.

### Compute Upgrade — Trino or Spark
Replace DuckDB with Trino for distributed SQL queries
when data volume outgrows a single machine. All dbt
models continue to work unchanged — only the connection
profile is updated.

### Streaming Ingestion
Replace hourly batch ingestion with real-time streaming:
- Apache Kafka for message queuing
- Flink or Spark Structured Streaming for processing
- Near real-time airport condition updates

### Monitoring and Alerting
- Dagster Cloud or self-hosted Dagster+ for pipeline monitoring
- PagerDuty or Slack alerts on pipeline failures
- Data SLA tracking — alert if gold layer is not refreshed on schedule

### Cloud Deployment
- Deploy full stack to AWS or GCP
- Terraform infrastructure-as-code for reproducible deployment
- Kubernetes for container orchestration

---

## Non-Goals

SkyLake is intentionally NOT:

- A real-time flight tracking system
- A consumer weather application
- A replacement for professional aviation weather services
- A system that makes safety-critical decisions

SkyLake is a data engineering portfolio project that
demonstrates production patterns using real aviation data.

---

## Version History

See docs/changelog.md for detailed version history.
