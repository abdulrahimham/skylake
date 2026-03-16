"""
Dagster asset definitions for the SkyLake bronze layer.

Uses dagster-dbt integration to automatically create Dagster assets
from dbt models. Each dbt model becomes an observable, materializable
asset in the Dagster UI with full lineage tracking.
"""

from pathlib import Path

from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets

# Path to the dbt project
DBT_PROJECT_DIR = Path(__file__).parents[3] / "dbt" / "skylake_dbt"
DBT_MANIFEST_PATH = DBT_PROJECT_DIR / "target" / "manifest.json"


@dbt_assets(manifest=DBT_MANIFEST_PATH)
def skylake_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """
    Dagster assets for all dbt models in the skylake_dbt project.

    Reads the dbt manifest and creates one Dagster asset per dbt model.
    Currently includes: bronze_metar, bronze_taf.

    Running this asset executes dbt run against the full project.
    Logs stream in real time to the Dagster UI.
    """
    yield from dbt.cli(["run"], context=context).stream()
