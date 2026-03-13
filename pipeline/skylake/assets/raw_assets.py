"""
Dagster asset definitions for the SkyLake raw ingestion layer.

These assets fetch data from the NOAA AWC API and write it
to the immutable raw layer (data/raw/).

Assets:
    raw_metar - Fetches METAR observations for all configured airports
    raw_taf   - Fetches TAF forecasts for all configured airports
"""

from datetime import datetime, timezone

from dagster import (
    AssetExecutionContext,
    MetadataValue,
    asset,
)
from dotenv import load_dotenv

from ingestion.clients.noaa_client import get_airports_from_env
from ingestion.writers.raw_writer import write_raw_metar, write_raw_taf
from pipeline.skylake.resources.noaa_resource import NOAAClientResource

load_dotenv()


@asset(
    group_name="raw",
    compute_kind="python",
    description="Raw METAR observations fetched from NOAA AWC API",
)
def raw_metar(context: AssetExecutionContext, noaa: NOAAClientResource):
    """
    Fetch raw METAR observations and write to the raw layer.

    Fetches the last 2 hours of METAR observations for all
    configured airports and writes each record as a date-partitioned
    JSON file to data/raw/metar/YYYY/MM/DD/.
    """
    ingested_at = datetime.now(timezone.utc)
    airports = get_airports_from_env()
    client = noaa.get_client()

    context.log.info(f"Fetching METARs for {len(airports)} airports: {', '.join(airports)}")

    metars = client.get_metars(airports)
    context.log.info(f"Received {len(metars)} METAR records from NOAA API")

    if not metars:
        context.log.warning("No METAR records received — skipping write")
        return

    paths = write_raw_metar(metars, ingested_at=ingested_at)
    context.log.info(f"Wrote {len(paths)} METAR files to raw layer")

    context.add_output_metadata({
        "airports": MetadataValue.text(", ".join(airports)),
        "records_fetched": MetadataValue.int(len(metars)),
        "files_written": MetadataValue.int(len(paths)),
        "ingested_at": MetadataValue.text(ingested_at.isoformat()),
        "sample_path": MetadataValue.text(str(paths[0]) if paths else "none"),
    })


@asset(
    group_name="raw",
    compute_kind="python",
    description="Raw TAF forecasts fetched from NOAA AWC API",
)
def raw_taf(context: AssetExecutionContext, noaa: NOAAClientResource):
    """
    Fetch raw TAF forecasts and write to the raw layer.

    Fetches the current TAF forecast for all configured airports
    and writes each record as a date-partitioned JSON file to
    data/raw/taf/YYYY/MM/DD/.
    """
    ingested_at = datetime.now(timezone.utc)
    airports = get_airports_from_env()
    client = noaa.get_client()

    context.log.info(f"Fetching TAFs for {len(airports)} airports: {', '.join(airports)}")

    tafs = client.get_tafs(airports)
    context.log.info(f"Received {len(tafs)} TAF records from NOAA API")

    if not tafs:
        context.log.warning("No TAF records received — skipping write")
        return

    paths = write_raw_taf(tafs, ingested_at=ingested_at)
    context.log.info(f"Wrote {len(paths)} TAF files to raw layer")

    context.add_output_metadata({
        "airports": MetadataValue.text(", ".join(airports)),
        "records_fetched": MetadataValue.int(len(tafs)),
        "files_written": MetadataValue.int(len(paths)),
        "ingested_at": MetadataValue.text(ingested_at.isoformat()),
        "sample_path": MetadataValue.text(str(paths[0]) if paths else "none"),
    })
