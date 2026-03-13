"""
Dagster schedules for SkyLake pipeline.

Defines when pipeline jobs run automatically.
All times are in UTC.

Schedules:
    hourly_raw_ingestion_schedule - runs raw_metar + raw_taf every hour
"""

from dagster import define_asset_job, schedule

# ── Job definitions ───────────────────────────────────────────────────────────

raw_ingestion_job = define_asset_job(
    name="raw_ingestion_job",
    selection=["raw_metar", "raw_taf"],
    description="Fetches METARs and TAFs from NOAA AWC API and writes to raw layer.",
)

# ── Schedule definitions ──────────────────────────────────────────────────────

@schedule(
    cron_schedule="0 * * * *",
    job=raw_ingestion_job,
    description="Run raw ingestion every hour on the hour (UTC).",
)
def hourly_raw_ingestion_schedule(context):
    """
    Hourly schedule for raw METAR and TAF ingestion.

    Fires at the top of every hour (00:00, 01:00, 02:00 ... UTC).
    Materializes raw_metar and raw_taf assets in sequence.
    """
    return {}
