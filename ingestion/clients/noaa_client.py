"""
NOAA Aviation Weather Center API client.

Fetches METARs and TAFs from the official NOAA AWC API.
No authentication required — public government data.

API docs: https://aviationweather.gov/api/docs/
Base URL: https://aviationweather.gov/api/data/
"""

import logging
import os

from ingestion.clients.base_client import BaseClient

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

NOAA_BASE_URL = "https://aviationweather.gov/api/data"

# Default airports to monitor — 8 major U.S. hubs across different climate regions
# Override by setting SKYLAKE_AIRPORTS in .env
DEFAULT_AIRPORTS = [
    "KJFK",  # New York — Northeast, fog and snow
    "KLAX",  # Los Angeles — marine layer, low ceilings
    "KORD",  # Chicago — severe weather, crosswinds
    "KATL",  # Atlanta — thunderstorms, humidity
    "KDFW",  # Dallas — wind, severe storms
    "KSEA",  # Seattle — rain, low ceilings
    "KDEN",  # Denver — snow, high altitude wind
    "KMIA",  # Miami — subtropical humidity, storms
]


def get_airports_from_env() -> list[str]:
    """
    Load airport list from environment variable.
    Falls back to DEFAULT_AIRPORTS if not set.
    """
    env_airports = os.getenv("SKYLAKE_AIRPORTS", "")
    if env_airports:
        airports = [a.strip().upper() for a in env_airports.split(",")]
        logger.info(f"Loaded {len(airports)} airports from SKYLAKE_AIRPORTS env var")
        return airports
    logger.info(f"Using default airport list ({len(DEFAULT_AIRPORTS)} airports)")
    return DEFAULT_AIRPORTS


# ── Client ────────────────────────────────────────────────────────────────────

class NOAAClient(BaseClient):
    """
    Client for NOAA Aviation Weather Center API.

    Fetches METARs (actual observations) and TAFs (forecasts)
    for a list of airports. Returns raw JSON responses for
    storage in the raw layer.

    Inherits HTTP connection handling from BaseClient.
    """

    def __init__(self, timeout: int = 30) -> None:
        super().__init__(base_url=NOAA_BASE_URL, timeout=timeout)
        logger.info("NOAAClient initialized")

    def get_metars(
        self,
        airport_ids: list[str],
        hours: int = 2,
    ) -> list[dict]:
        """
        Fetch METAR observations for a list of airports.

        Args:
            airport_ids: List of ICAO airport codes (e.g. ['KJFK', 'KLAX'])
            hours:       Number of hours of history to fetch. Defaults to 2.

        Returns:
            List of raw METAR observation dicts from NOAA API.
        """
        params = {
            "ids": ",".join(airport_ids),
            "format": "json",
            "taf": "false",
            "hours": hours,
        }
        logger.info(f"Fetching METARs for {len(airport_ids)} airports (last {hours}h)")
        data = self.get("metar", params=params)

        # NOAA returns either a list directly or wraps in a dict
        if isinstance(data, list):
            logger.info(f"Received {len(data)} METAR records")
            return data
        return []

    def get_tafs(self, airport_ids: list[str]) -> list[dict]:
        """
        Fetch TAF forecasts for a list of airports.

        Args:
            airport_ids: List of ICAO airport codes

        Returns:
            List of raw TAF forecast dicts from NOAA API.
        """
        params = {
            "ids": ",".join(airport_ids),
            "format": "json",
        }
        logger.info(f"Fetching TAFs for {len(airport_ids)} airports")
        data = self.get("taf", params=params)

        if isinstance(data, list):
            logger.info(f"Received {len(data)} TAF records")
            return data
        return []


# ── Manual test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    client = NOAAClient()
    airports = get_airports_from_env()

    print("\n" + "=" * 60)
    print("SkyLake — NOAA AWC API Test")
    print("=" * 60)

    # Test METAR fetch
    print(f"\nFetching METARs for: {', '.join(airports)}")
    metars = client.get_metars(airports)
    print(f"Received {len(metars)} METAR records")
    if metars:
        print("\nFirst METAR record:")
        print(json.dumps(metars[0], indent=2))

    # Test TAF fetch
    print(f"\nFetching TAFs for: {', '.join(airports)}")
    tafs = client.get_tafs(airports)
    print(f"Received {len(tafs)} TAF records")
    if tafs:
        print("\nFirst TAF record:")
        print(json.dumps(tafs[0], indent=2))

    print("\n" + "=" * 60)
    print("API test complete")
    print("=" * 60)
