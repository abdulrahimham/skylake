"""
Dagster resource wrapping the NOAA AWC API client.

Resources in Dagster are shared, configurable dependencies
that are injected into assets at runtime. This resource
wraps the NOAAClient and makes it available to all raw assets.
"""

from dagster import ConfigurableResource

from ingestion.clients.noaa_client import NOAAClient


class NOAAClientResource(ConfigurableResource):
    """
    Dagster resource for the NOAA Aviation Weather Center API.

    Wraps NOAAClient to make it injectable and configurable
    via Dagster's resource system.

    Configuration:
        timeout: HTTP request timeout in seconds (default: 30)
    """

    timeout: int = 30

    def get_client(self) -> NOAAClient:
        """Return a configured NOAAClient instance."""
        return NOAAClient(timeout=self.timeout)
