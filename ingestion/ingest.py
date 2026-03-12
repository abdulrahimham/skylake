"""
SkyLake main ingestion script.

Fetches METARs and TAFs from NOAA AWC API and writes
them to the immutable raw layer (data/raw/).

This script is called by:
- make ingest          (manual run)
- Dagster raw assets   (scheduled pipeline run)

Usage:
    uv run python -m ingestion.ingest
"""

import logging
import time
from datetime import datetime, timezone

from dotenv import load_dotenv

from ingestion.clients.noaa_client import NOAAClient, get_airports_from_env
from ingestion.utils.logging import setup_logging
from ingestion.writers.raw_writer import write_raw_metar, write_raw_taf

# Load .env file
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def run_ingestion() -> dict:
    """
    Run a full ingestion cycle — fetch METARs and TAFs, write to raw layer.

    Returns:
        Summary dict with counts of records fetched and files written.
    """
    ingested_at = datetime.now(timezone.utc)
    start_time = time.time()

    logger.info("=" * 50)
    logger.info("SkyLake ingestion starting")
    logger.info(f"Ingestion time: {ingested_at.isoformat()}")
    logger.info("=" * 50)

    client = NOAAClient()
    airports = get_airports_from_env()
    logger.info(f"Airports: {', '.join(airports)}")

    summary = {
        "ingested_at": ingested_at.isoformat(),
        "airports": airports,
        "metar_records": 0,
        "taf_records": 0,
        "metar_files": 0,
        "taf_files": 0,
        "errors": [],
    }

    # ── Fetch and write METARs ─────────────────────────────────
    try:
        logger.info("Fetching METARs...")
        metars = client.get_metars(airports)
        summary["metar_records"] = len(metars)

        if metars:
            metar_files = write_raw_metar(metars, ingested_at=ingested_at)
            summary["metar_files"] = len(metar_files)
            logger.info(f"Wrote {len(metar_files)} METAR files")
        else:
            logger.warning("No METAR records received from NOAA API")

    except Exception as e:
        error_msg = f"METAR ingestion failed: {e}"
        logger.error(error_msg)
        summary["errors"].append(error_msg)

    # ── Fetch and write TAFs ───────────────────────────────────
    try:
        logger.info("Fetching TAFs...")
        tafs = client.get_tafs(airports)
        summary["taf_records"] = len(tafs)

        if tafs:
            taf_files = write_raw_taf(tafs, ingested_at=ingested_at)
            summary["taf_files"] = len(taf_files)
            logger.info(f"Wrote {len(taf_files)} TAF files")
        else:
            logger.warning("No TAF records received from NOAA API")

    except Exception as e:
        error_msg = f"TAF ingestion failed: {e}"
        logger.error(error_msg)
        summary["errors"].append(error_msg)

    # ── Summary ───────────────────────────────────────────────
    elapsed = time.time() - start_time
    logger.info("=" * 50)
    logger.info(f"Ingestion complete in {elapsed:.1f}s")
    logger.info(f"METARs: {summary['metar_records']} records -> {summary['metar_files']} files")
    logger.info(f"TAFs:   {summary['taf_records']} records -> {summary['taf_files']} files")
    if summary["errors"]:
        logger.error(f"Errors: {summary['errors']}")
    logger.info("=" * 50)

    return summary


if __name__ == "__main__":
    run_ingestion()
