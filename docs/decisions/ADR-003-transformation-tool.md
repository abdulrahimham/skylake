# ADR-003: Transformation Tool — dbt-core

**Date:** 2026-03-12
**Status:** Accepted
**Deciders:** abdulrahimham

---

## Context

SkyLake requires a transformation tool that can:
- Clean and enrich raw aviation weather data
- Model bronze, silver, and gold layer tables
- Run automated tests on the data
- Generate documentation automatically
- Be version controlled alongside the rest of the codebase

---

## Decision

Use **dbt-core** with the **dbt-duckdb** adapter for all
data transformation logic.

---

## Reasoning

dbt is the industry standard for SQL-based data transformation.
It turns simple SQL SELECT statements into fully managed,
tested, and documented data models.

Key advantages for SkyLake:
- Write transformations as plain SQL — no boilerplate code
- Built-in testing (not-null, unique, accepted values, relationships)
- Auto-generates data documentation and lineage diagrams
- Models are modular and reusable
- Widely used in industry — directly transferable skill

The dbt-duckdb adapter means dbt works natively with our
DuckDB + Parquet storage layer with zero extra configuration.

---

## Alternatives Considered

| Option | Reason Rejected |
|---|---|
| Raw Python + Pandas | Works but produces untestable, undocumented transformation scripts. No lineage. Hard to maintain. |
| Apache Spark | Powerful but over-engineered for this data volume. Requires cluster infrastructure. Designed for terabytes not megabytes. |
| SQLMesh | Modern dbt alternative. Less mature ecosystem and fewer learning resources available. |

---

## How dbt Works in SkyLake

Each dbt model is a .sql file containing a single SELECT statement.
dbt handles CREATE TABLE, INSERT, and dependency ordering automatically.

Example:
- bronze_metar.sql selects from raw Parquet files
- silver_metar_parsed.sql selects from ref('bronze_metar')
- gold_airport_conditions.sql selects from ref('silver_metar_parsed')

The ref() function tells dbt about dependencies so it always
runs models in the correct order.

---

## Consequences

- All transformation logic lives in dbt/skylake_dbt/models/
- Models organized into bronze/, silver/, and gold/ subfolders
- dbt tests run automatically in CI pipeline
- dbt docs generate a browsable data catalog
