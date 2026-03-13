"""
SkyLake Dagster definitions.

This module is the entry point for the Dagster pipeline.
It wires together all assets, resources, schedules, and sensors
into a single Definitions object that Dagster reads at startup.
"""

from dagster import Definitions

from pipeline.skylake.assets.raw_assets import raw_metar, raw_taf
from pipeline.skylake.resources.noaa_resource import NOAAClientResource
from pipeline.skylake.schedules.schedules import (
    hourly_raw_ingestion_schedule,
    raw_ingestion_job,
)

defs = Definitions(
    assets=[raw_metar, raw_taf],
    jobs=[raw_ingestion_job],
    schedules=[hourly_raw_ingestion_schedule],
    resources={
        "noaa": NOAAClientResource(),
    },
)
