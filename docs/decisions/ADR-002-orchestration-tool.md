# ADR-002: Orchestration Tool — Dagster over Apache Airflow

**Date:** 2026-03-12
**Status:** Accepted
**Deciders:** abdulrahimham

---

## Context

SkyLake requires an orchestration tool that can:
- Schedule hourly ingestion jobs
- Run transformation steps in the correct order
- Monitor pipeline health and alert on failures
- Track which data assets exist and when they were last updated
- Be runnable locally without heavy infrastructure

---

## Decision

Use **Dagster** as the pipeline orchestration tool.

---

## Reasoning

Dagster uses a software-defined assets model. Instead of defining
tasks (what to do), you define assets (what data should exist). This
means the pipeline is self-documenting — looking at the asset graph
immediately shows what data exists and how it was produced.

Key advantages for SkyLake:
- Built-in asset lineage tracking (see exactly where data came from)
- Modern UI with observability out of the box
- Easier local development than Airflow
- Asset-based model matches how data engineers actually think

---

## Alternatives Considered

| Option | Reason Rejected |
|---|---|
| Apache Airflow | Task-based model is less intuitive. Requires separate metadata DB, scheduler, webserver, and worker processes. Heavy local setup. |
| Prefect | Similar modern alternative to Dagster. Either would work. Dagster chosen for stronger asset lineage features. |
| Cron + Python scripts | Works for simple cases but no UI, no monitoring, no retry logic, no lineage tracking. Not appropriate for a production-style project. |

---

## Future Considerations

Airflow is still dominant in enterprise environments. The concepts
learned in Dagster — DAGs, scheduling, sensors, retries — transfer
directly to Airflow. Completing this project in Dagster then spending
time on Airflow's quickstart is the recommended learning path.

---

## Consequences

- Pipeline logic lives in dagster/skylake/assets/
- Each data layer (raw, bronze, silver, gold) is a Dagster asset
- Dagster UI available at http://localhost:3000 when running locally
- Scheduling and sensors defined in dagster/skylake/schedules/
