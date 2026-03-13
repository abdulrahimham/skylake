"""
Unit tests for ingestion/clients/base_client.py

Tests HTTP success, timeout, status errors, and network errors
without making any real network calls.
"""

import pytest
import httpx
from unittest.mock import MagicMock, patch

from ingestion.clients.base_client import BaseClient


class TestBaseClient:

    def setup_method(self):
        """Create a fresh client before each test."""
        self.client = BaseClient(base_url="https://api.example.com", timeout=10)

    def test_init_strips_trailing_slash(self):
        """Base URL should have trailing slash stripped."""
        client = BaseClient(base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"

    def test_init_stores_timeout(self):
        """Timeout should be stored on the client."""
        client = BaseClient(base_url="https://api.example.com", timeout=60)
        assert client.timeout == 60

    def test_get_success(self):
        """Successful GET returns parsed JSON."""
        with patch("httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"status": "ok"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = self.client.get("endpoint")

            assert result == {"status": "ok"}
            mock_get.assert_called_once_with(
                "https://api.example.com/endpoint",
                params=None,
                timeout=10,
            )

    def test_get_with_params(self):
        """GET passes query parameters correctly."""
        with patch("httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            self.client.get("metar", params={"ids": "KJFK", "format": "json"})

            mock_get.assert_called_once_with(
                "https://api.example.com/metar",
                params={"ids": "KJFK", "format": "json"},
                timeout=10,
            )

    def test_get_timeout_raises_connection_error(self):
        """TimeoutException is converted to ConnectionError."""
        with patch("httpx.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("timed out")

            with pytest.raises(ConnectionError, match="timed out"):
                self.client.get("endpoint")

    def test_get_http_error_raises_value_error(self):
        """Non-200 HTTP response raises ValueError with status code."""
        with patch("httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "not found",
                request=MagicMock(),
                response=MagicMock(status_code=404, text="Not Found"),
            )
            mock_get.return_value = mock_response

            with pytest.raises(ValueError, match="404"):
                self.client.get("endpoint")

    def test_get_network_error_raises_connection_error(self):
        """Network failure raises ConnectionError."""
        with patch("httpx.get") as mock_get:
            mock_get.side_effect = httpx.RequestError("network failure", request=MagicMock())

            with pytest.raises(ConnectionError, match="Network error"):
                self.client.get("endpoint")
