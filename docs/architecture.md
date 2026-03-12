# SkyLake — Architecture

> Documentation in progress. Full architecture writeup coming in Phase 0 Day 5.

## Overview

SkyLake follows a medallion lakehouse architecture with four storage layers:
- **Raw** — immutable, append-only ingested data
- **Bronze** — structured, minimally cleaned Parquet
- **Silver** — enriched, deduplicated, business-logic applied
- **Gold** — analytical outputs and data products
