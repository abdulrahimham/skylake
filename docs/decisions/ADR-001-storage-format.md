# ADR-001: Storage Format — DuckDB + Parquet for MVP

**Date:** 2026-03-12
**Status:** Accepted
**Deciders:** abdulrahimham

---

## Context

SkyLake requires a storage layer that can:
- Store immutable raw files safely
- Support analytical (columnar) query patterns efficiently
- Run locally without infrastructure dependencies for MVP development
- Be upgradeable to a distributed object store later

---

## Decision

Use **Apache Parquet** as the on-disk file format for all layers (raw, bronze, silver, gold),
with **DuckDB** as the query engine during MVP development.

---

## Reasoning

**Parquet** is the de facto standard for analytical data storage. It is:
- Columnar — efficient for the aggregation-heavy queries this project runs
- Compressed — significantly smaller than CSV for numerical weather data
- Interoperable — readable by Spark, Trino, BigQuery, DuckDB, and Pandas without conversion
- Immutable by nature — files are written once and not modified

**DuckDB** provides:
- Zero-infrastructure SQL analytics over Parquet files
- Native integration with dbt-duckdb
- Performance comparable to a small Spark cluster for this data volume
- A clear upgrade path: swap the DuckDB engine for Trino or Spark without changing Parquet files

---

## Alternatives Considered

| Option | Reason Rejected |
|---|---|
| PostgreSQL | Row-oriented, not suited for analytical workloads; heavier infrastructure |
| SQLite | Not designed for analytical queries; limited type support |
| CSV files | No compression, no schema enforcement, no columnar access |
| Delta Lake / Iceberg (now) | Correct long-term choice but requires S3/MinIO; out of scope for MVP |

---

## Future Upgrade Path

When this project scales beyond MVP:
1. Replace local data/ directory with MinIO (S3-compatible object store)
2. Layer Apache Iceberg table format over Parquet for ACID transactions and time travel
3. Replace DuckDB with Trino or Spark for distributed query execution
4. This migration will not require changing dbt models — only connection profiles

---

## Consequences

- All data files are Parquet from day one, ensuring the upgrade path remains clean
- DuckDB is a dev/MVP dependency only; it does not appear in gold-layer APIs
- The data/ directory is gitignored; only schema definitions and seeds are versioned
