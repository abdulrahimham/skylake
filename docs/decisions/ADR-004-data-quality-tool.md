# ADR-004: Data Quality Tool — Soda Core

**Date:** 2026-03-12
**Status:** Accepted
**Deciders:** abdulrahimham

---

## Context

SkyLake ingests real government weather data from an external API.
External data sources can have:
- Missing fields or unexpected nulls
- Values outside expected ranges
- Schema changes without warning
- Duplicate records
- Delayed or missing updates

We need a way to catch these issues before bad data
propagates through the bronze, silver, and gold layers.

---

## Decision

Use **Soda Core** for data quality checks at the bronze
layer entry point, combined with **dbt tests** at the
silver and gold layers.

---

## Reasoning

Soda Core and dbt tests serve different purposes and
work best together:

Soda Core runs BEFORE dbt transformations. It checks
the raw incoming data at the bronze layer and catches
issues at the earliest possible point. If the NOAA API
returns malformed data, Soda catches it before it ever
touches a dbt model.

dbt tests run AFTER transformations. They verify that
the transformation logic produced correct results —
no nulls in required fields, no duplicate airport codes,
values within expected ranges.

Using both creates defense in depth — multiple quality
gates at different points in the pipeline.

---

## Alternatives Considered

| Option | Reason Rejected |
|---|---|
| dbt tests only | Only catches issues after transformation. Bad source data could silently corrupt models before tests run. |
| Great Expectations | More powerful but significantly more complex to set up and maintain. Better suited for larger teams. |
| Pandera | Python-based schema validation. Good but less suited for SQL/DuckDB workflows. |
| Manual checks | Not automated, not scalable, easy to forget. |

---

## How Soda Works in SkyLake

Soda checks are defined in simple YAML files in soda/checks/.
Example check for bronze_metar:

  checks for bronze_metar:
    - row_count > 0
    - missing_count(station_id) = 0
    - invalid_count(wind_speed_kt) < 10
    - freshness(observation_time) < 2h

These run automatically after ingestion and before
dbt transformations begin.

---

## Consequences

- Soda checks live in soda/checks/
- Checks run as part of the Dagster pipeline after ingestion
- Failed checks block downstream dbt transformations
- dbt tests provide a second quality layer at silver and gold
