# SkyLake — Architecture

## System Overview

SkyLake is a batch data lakehouse that ingests official aviation
weather data from NOAA's Aviation Weather Center API on an hourly
schedule. Raw data is stored immutably and transformed through
bronze, silver, and gold layers to produce airport-level operational
risk scores, forecast accuracy metrics, and weather event detection
outputs.

The system is designed to reflect production data engineering
standards: layered storage, automated data quality checks,
orchestrated pipeline runs, CI/CD, and full documentation.

---

## Data Flow
```
NOAA Aviation Weather Center API
https://aviationweather.gov/api/data/
        │
        │  Python + httpx
        │  Fetches METARs and TAFs every hour
        │  for 8 major U.S. airports
        ▼
┌─────────────────────────────────┐
│         RAW LAYER               │
│  data/raw/metar/YYYY/MM/DD/     │
│  data/raw/taf/YYYY/MM/DD/       │
│                                 │
│  • Immutable JSON files         │
│  • Never modified after write   │
│  • Partitioned by date          │
└─────────────────────────────────┘
        │
        │  Python ingestion parsers
        │  Parse JSON → typed columns
        ▼
┌─────────────────────────────────┐
│        BRONZE LAYER             │
│  data/bronze/                   │
│                                 │
│  • Structured Parquet files     │
│  • Minimal cleaning only        │
│  • Soda Core checks run here    │
│  • One row per raw observation  │
└─────────────────────────────────┘
        │
        │  dbt models
        │  Clean, deduplicate, enrich, join
        ▼
┌─────────────────────────────────┐
│        SILVER LAYER             │
│  data/silver/                   │
│                                 │
│  • Cleaned and typed data       │
│  • Nulls handled                │
│  • Units standardized           │
│  • METAR + TAF joined           │
│  • dbt tests enforce quality    │
└─────────────────────────────────┘
        │
        │  dbt models
        │  Produce analytical outputs
        ▼
┌─────────────────────────────────┐
│         GOLD LAYER              │
│  data/gold/                     │
│                                 │
│  • Airport hourly conditions    │
│  • Forecast accuracy scores     │
│  • Low visibility events        │
│  • Wind disruption windows      │
│  • Airport risk scores (0-100)  │
└─────────────────────────────────┘
        │
        │  Streamlit reads DuckDB views
        ▼
┌─────────────────────────────────┐
│       SERVING LAYER             │
│  localhost:8501                 │
│                                 │
│  • Airport risk dashboard       │
│  • Forecast accuracy charts     │
│  • Weather event timeline       │
└─────────────────────────────────┘
```

---

## Layer Contracts

Each layer has a contract — a guarantee about what kind of
data it contains. Downstream layers can rely on these guarantees.

| Layer | Contract |
|---|---|
| Raw | Exactly what the API returned. Never modified. Append-only. |
| Bronze | Structured and typed. Soda Core checks have passed. One row per observation. |
| Silver | Cleaned, deduplicated, nulls handled, units standardized. dbt tests pass. |
| Gold | Analytical outputs. Optimized for reading. Ready for dashboard consumption. |

---

## Technology Stack

| Layer | Tool | Decision |
|---|---|---|
| Ingestion | Python + httpx | See ADR-005 |
| Orchestration | Dagster | See ADR-002 |
| Transformation | dbt-core + dbt-duckdb | See ADR-003 |
| Storage | DuckDB + Parquet | See ADR-001 |
| Data Quality | Soda Core + dbt tests | See ADR-004 |
| Serving | Streamlit | Lightweight demo layer |
| Containerization | Docker + Compose | Full reproducibility |
| CI | GitHub Actions | Automated testing on push |
| Dependencies | uv | Fast, modern, lock-file based |

Full reasoning for each decision in docs/decisions/

---

## Orchestration Flow

Dagster runs the full pipeline on an hourly schedule:
```
1. raw_metar_asset      — fetch METARs from NOAA API
2. raw_taf_asset        — fetch TAFs from NOAA API
3. bronze_metar_asset   — parse raw METAR JSON to Parquet
4. bronze_taf_asset     — parse raw TAF JSON to Parquet
5. soda_checks          — validate bronze data quality
6. dbt_silver_models    — run silver layer transformations
7. dbt_gold_models      — run gold layer transformations
```

If Soda checks fail at step 5, steps 6 and 7 do not run.
Bad data never reaches the gold layer.

---

## Repository Structure
```
skylake/
├── dagster/          # Orchestration — assets, jobs, schedules
├── dbt/              # Transformation — bronze/silver/gold models
├── ingestion/        # Ingestion — API client, parsers, writers
├── soda/             # Data quality — bronze layer checks
├── streamlit/        # Serving — dashboard and pages
├── data/             # Data files — gitignored
├── docker/           # Dockerfiles for each service
├── docs/             # All project documentation
│   └── decisions/    # Architecture Decision Records
├── tests/            # Unit and integration tests
├── .github/          # GitHub Actions CI workflows
├── docker-compose.yml
├── Makefile
└── pyproject.toml
```

---

## Data Volume Estimates (MVP)

| Metric | Estimate |
|---|---|
| Airports monitored | 8 |
| METAR records per day | ~192 (8 airports x 24 hours) |
| TAF records per day | ~32 (8 airports x 4 forecasts) |
| Raw storage per day | ~500KB |
| Raw storage per year | ~180MB |

DuckDB handles this volume with ease on a single laptop.
No distributed compute required at MVP scale.

---

## Future Upgrade Path

The MVP is designed with a clear production upgrade path.
Each upgrade is independent — they can be done in any order.

| Upgrade | What Changes | What Stays the Same |
|---|---|---|
| Local → MinIO/S3 | Storage location | Parquet format, dbt models |
| DuckDB → Trino | Query engine | Parquet files, dbt SQL |
| Parquet → Iceberg | Table format | Underlying Parquet files |
| Batch → Streaming | Ingestion layer | Bronze/silver/gold models |

The key design principle: storage format, query engine, and
table format are all independent. Upgrading one does not
require rewriting the others.

---

## Airports in Scope (MVP)

| ICAO | Airport | City | Climate |
|---|---|---|---|
| KJFK | John F. Kennedy Intl | New York | Northeast — fog, snow, wind |
| KLAX | Los Angeles Intl | Los Angeles | West Coast — marine layer |
| KORD | O'Hare Intl | Chicago | Midwest — severe weather |
| KATL | Hartsfield-Jackson | Atlanta | Southeast — thunderstorms |
| KDFW | Dallas/Fort Worth Intl | Dallas | Southern Plains — wind, storms |
| KSEA | Seattle-Tacoma Intl | Seattle | Pacific NW — rain, low ceilings |
| KDEN | Denver Intl | Denver | High altitude — snow, wind |
| KMIA | Miami Intl | Miami | Subtropical — humidity, storms |

These airports were selected to maximize weather variety
across different U.S. climate regions.
