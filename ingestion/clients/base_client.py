"""
Base HTTP client for SkyLake ingestion layer.

Provides a reusable foundation for all API clients in the project.
Handles timeouts, error responses, and basic logging.
"""

import logging

import httpx

logger = logging.getLogger(__name__)


class BaseClient:
    """
    Generic HTTP client base class.

    All SkyLake API clients inherit from this class.
    Handles connection logic, timeouts, and error handling
    so individual clients only need to implement source-specific logic.
    """

    def __init__(self, base_url: str, timeout: int = 30) -> None:
        """
        Initialize the base client.

        Args:
            base_url: Root URL of the API (e.g. https://aviationweather.gov/api/data)
            timeout:  Request timeout in seconds. Defaults to 30.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        logger.debug(f"Initialized client for {self.base_url}")

    def get(self, endpoint: str, params: dict | None = None) -> dict | list:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint path (e.g. 'metar')
            params:   Query parameters as a dictionary

        Returns:
            Parsed JSON response as dict or list

        Raises:
            ConnectionError: On timeout or network failure
            ValueError:      On non-200 HTTP response
        """
        url = f"{self.base_url}/{endpoint}"
        logger.debug(f"GET {url} params={params}")

        try:
            response = httpx.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            raise ConnectionError(
                f"Request to {url} timed out after {self.timeout}s"
            )
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"HTTP {e.response.status_code} from {url}: {e.response.text[:200]}"
            )
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Network error requesting {url}: {e}"
            )
