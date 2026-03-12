"""
Raw layer writer for SkyLake ingestion pipeline.

Writes immutable raw JSON files to the data/raw/ directory,
partitioned by data type and date (YYYY/MM/DD).

Design principles:
- Files are written once and never modified (immutable raw layer)
- Partitioned by date for efficient downstream processing
- Each file is human-readable JSON for easy debugging
- Filenames include airport code and timestamp for uniqueness
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

DATA_DIR = Path(os.getenv("SKYLAKE_DATA_DIR", "./data"))
RAW_DIR = DATA_DIR / "raw"


# ── Writer ────────────────────────────────────────────────────────────────────

def write_raw_metar(records: list[dict], ingested_at: datetime | None = None) -> list[Path]:
    """
    Write raw METAR records to the raw layer.

    Each record is written as a separate JSON file, partitioned
    by the observation date (YYYY/MM/DD).

    Args:
        records:     List of raw METAR dicts from NOAA API
        ingested_at: Ingestion timestamp. Defaults to now (UTC).

    Returns:
        List of file paths written.
    """
    if ingested_at is None:
        ingested_at = datetime.now(timezone.utc)

    written = []
    for record in records:
        path = _write_record(
            record=record,
            data_type="metar",
            airport_id=record.get("icaoId", "UNKNOWN"),
            obs_time=_parse_obs_time(record),
            ingested_at=ingested_at,
        )
        written.append(path)

    logger.info(f"Wrote {len(written)} raw METAR files to {RAW_DIR / 'metar'}")
    return written


def write_raw_taf(records: list[dict], ingested_at: datetime | None = None) -> list[Path]:
    """
    Write raw TAF records to the raw layer.

    Each record is written as a separate JSON file, partitioned
    by the issue date (YYYY/MM/DD).

    Args:
        records:     List of raw TAF dicts from NOAA API
        ingested_at: Ingestion timestamp. Defaults to now (UTC).

    Returns:
        List of file paths written.
    """
    if ingested_at is None:
        ingested_at = datetime.now(timezone.utc)

    written = []
    for record in records:
        path = _write_record(
            record=record,
            data_type="taf",
            airport_id=record.get("icaoId", "UNKNOWN"),
            obs_time=_parse_issue_time(record),
            ingested_at=ingested_at,
        )
        written.append(path)

    logger.info(f"Wrote {len(written)} raw TAF files to {RAW_DIR / 'taf'}")
    return written


# ── Internal helpers ──────────────────────────────────────────────────────────

def _write_record(
    record: dict,
    data_type: str,
    airport_id: str,
    obs_time: datetime,
    ingested_at: datetime,
) -> Path:
    """
    Write a single record to a date-partitioned JSON file.

    File path pattern:
        data/raw/{data_type}/YYYY/MM/DD/{data_type}_{airport}_{HHMMSS}.json

    Args:
        record:      Raw dict from NOAA API
        data_type:   'metar' or 'taf'
        airport_id:  ICAO airport code
        obs_time:    Observation or issue time (used for partitioning)
        ingested_at: When ingestion ran

    Returns:
        Path to the written file.
    """
    # Build date-partitioned directory path
    partition_dir = (
        RAW_DIR
        / data_type
        / obs_time.strftime("%Y")
        / obs_time.strftime("%m")
        / obs_time.strftime("%d")
    )
    partition_dir.mkdir(parents=True, exist_ok=True)

    # Build unique filename
    timestamp_str = obs_time.strftime("%H%M%S")
    filename = f"{data_type}_{airport_id}_{timestamp_str}.json"
    filepath = partition_dir / filename

    # Add ingestion metadata to the record before writing
    enriched_record = {
        "_skylake_meta": {
            "ingested_at": ingested_at.isoformat(),
            "data_type": data_type,
            "source": "noaa_awc",
        },
        **record,
    }

    # Write as human-readable JSON
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(enriched_record, f, indent=2, ensure_ascii=False)

    logger.debug(f"Wrote {filepath}")
    return filepath


def _parse_obs_time(metar: dict) -> datetime:
    """
    Extract observation time from a METAR record.
    Falls back to current UTC time if not found.
    """
    report_time = metar.get("reportTime")
    if report_time:
        try:
            return datetime.fromisoformat(report_time.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass
    return datetime.now(timezone.utc)


def _parse_issue_time(taf: dict) -> datetime:
    """
    Extract issue time from a TAF record.
    Falls back to current UTC time if not found.
    """
    issue_time = taf.get("issueTime")
    if issue_time:
        try:
            return datetime.fromisoformat(issue_time.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass
    return datetime.now(timezone.utc)
