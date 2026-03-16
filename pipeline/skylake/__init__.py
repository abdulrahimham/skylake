"""
SkyLake Dagster definitions.

This module is the entry point for the Dagster pipeline.
It wires together all assets, resources, schedules, and sensors
into a single Definitions object that Dagster reads at startup.
"""

from pathlib import Path

from dagster import Definitions
from dagster_dbt import DbtCliResource

from pipeline.skylake.assets.raw_assets import raw_metar, raw_taf
from pipeline.skylake.assets.bronze_assets import skylake_dbt_assets
from pipeline.skylake.resources.noaa_resource import NOAAClientResource
from pipeline.skylake.schedules.schedules import (
    hourly_raw_ingestion_schedule,
    raw_ingestion_job,
)

DBT_PROJECT_DIR = Path(__file__).parents[2] / "dbt" / "skylake_dbt"

defs = Definitions(
    assets=[raw_metar, raw_taf, skylake_dbt_assets],
    jobs=[raw_ingestion_job],
    schedules=[hourly_raw_ingestion_schedule],
    resources={
        "noaa": NOAAClientResource(),
        "dbt": DbtCliResource(project_dir=str(DBT_PROJECT_DIR)),
    },
)
