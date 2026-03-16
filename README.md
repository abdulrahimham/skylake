# SkyLake: Airport Weather Operations Lakehouse

> An end-to-end data engineering project ingesting official aviation weather data
> (METARs, TAFs) from NOAA's Aviation Weather Center, storing it in an immutable
> raw layer, and transforming it through bronze → silver → gold layers to produce
> airport-level operational risk and forecast accuracy data products.

---

## Project Status

| Phase | Status |
|---|---|
| Phase 0 — Foundation | ✅ Complete |
| Phase 1 — Raw Ingestion | ✅ Complete |
| Phase 2 — Bronze Layer | ✅ Complete |
| Phase 3 — Silver Layer | ✅ Complete |
| Phase 4 — Gold Layer | 🟡 In Progress |
| Phase 5 — Orchestration | ⬜ Not Started |
| Phase 6 — Data Quality | ⬜ Not Started |
| Phase 7 — Serving Layer | ⬜ Not Started |
| Phase 8 — CI + Docker | ⬜ Not Started |
| Phase 9 — Docs + Polish | ⬜ Not Started |

---

## Architecture Overview
```
NOAA Aviation Weather Center API
        │
        ▼
  [ Ingestion Layer ]      Python + httpx
        │  Raw JSON stored immutably
        ▼
  [ Raw Layer ]            data/raw/ (JSON partitioned by date)
        │
        ▼
  [ Bronze Layer ]         Structured Parquet → DuckDB
        │  Soda Core data quality checks
        ▼
  [ Silver Layer ]         dbt models — cleaned, enriched, joined
        │
        ▼
  [ Gold Layer ]           dbt models — analytical outputs
        │
        ▼
  [ Serving Layer ]        Streamlit dashboard
```

Full architecture documentation: [docs/architecture.md](docs/architecture.md)

---

## Data Products

| Product | Layer | Description |
|---|---|---|
| Airport Hourly Conditions | Gold | Visibility, wind, ceiling, flight category per airport per hour |
| Forecast Accuracy | Gold | TAF prediction vs METAR actual — scored per period |
| Low Visibility Events | Gold | IFR/LIFR event detection with duration |
| Wind Disruption Windows | Gold | High-wind event detection with peak gust |
| Airport Risk Score | Gold | Composite operational risk score (0–100) |

---

## Stack

| Tool | Role |
|---|---|
| Python + httpx | Data ingestion |
| Dagster | Orchestration and asset management |
| dbt-core | Transformation modeling |
| DuckDB + Parquet | MVP storage layer |
| Soda Core | Pre-transformation data quality |
| Streamlit | Demo serving layer |
| Docker + Compose | Full environment reproducibility |
| GitHub Actions | CI — lint, test, dbt compile on every push |
| uv | Python dependency management |

---

## Quickstart
```bash
git clone https://github.com/abdulrahimham/skylake.git
cd skylake
cp .env.example .env
make setup
make up
```

---

## Documentation

| Doc | Description |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Full system design |
| [docs/data_model.md](docs/data_model.md) | Layer-by-layer data model |
| [docs/data_dictionary.md](docs/data_dictionary.md) | Field definitions |
| [docs/ingestion_runbook.md](docs/ingestion_runbook.md) | How to run ingestion |
| [docs/decisions/](docs/decisions/) | Architecture Decision Records |
| [docs/roadmap.md](docs/roadmap.md) | Future development plan |
| [docs/changelog.md](docs/changelog.md) | Version history |

---

## Data Source

All weather data sourced from **NOAA's Aviation Weather Center (AWC)**
API: `https://aviationweather.gov/api/data/`
No API key required. Official U.S. government aviation weather data.

---

*Built as a portfolio data engineering project. Designed to reflect
production engineering standards including layered storage, orchestration,
data quality checks, CI, and full documentation.*
