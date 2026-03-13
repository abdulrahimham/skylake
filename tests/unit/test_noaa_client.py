"""
Unit tests for ingestion/clients/noaa_client.py

Tests METAR and TAF fetch methods, parameter construction,
and response handling without making real API calls.
"""

import pytest
from unittest.mock import patch

from ingestion.clients.noaa_client import NOAAClient, get_airports_from_env, DEFAULT_AIRPORTS


# ── Sample data ───────────────────────────────────────────────────────────────

MOCK_METAR = {
    "icaoId": "KJFK",
    "reportTime": "2026-03-12T23:00:00.000Z",
    "temp": 1.1,
    "dewp": 0.6,
    "wdir": 270,
    "wspd": 14,
    "visib": 2.5,
    "fltCat": "IFR",
    "wxString": "-SN BR",
}

MOCK_TAF = {
    "icaoId": "KJFK",
    "issueTime": "2026-03-12T22:26:00.000Z",
    "rawTAF": "TAF KJFK 122226Z 1224/1324 27015KT P6SM SCT030",
    "fcsts": [
        {"timeFrom": 1773352800, "timeTo": 1773360000, "wdir": 270, "wspd": 15}
    ],
}


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestNOAAClient:

    def setup_method(self):
        """Create a fresh client before each test."""
        self.client = NOAAClient()

    def test_get_metars_returns_list(self):
        """get_metars returns list of METAR dicts."""
        with patch.object(self.client, "get", return_value=[MOCK_METAR]):
            result = self.client.get_metars(["KJFK"])
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["icaoId"] == "KJFK"

    def test_get_metars_passes_correct_params(self):
        """get_metars calls the correct endpoint with correct params."""
        with patch.object(self.client, "get", return_value=[MOCK_METAR]) as mock_get:
            self.client.get_metars(["KJFK", "KLAX"])
            mock_get.assert_called_once_with(
                "metar",
                params={
                    "ids": "KJFK,KLAX",
                    "format": "json",
                    "taf": "false",
                    "hours": 2,
                },
            )

    def test_get_metars_joins_airport_ids(self):
        """Multiple airport IDs are joined into a comma-separated string."""
        with patch.object(self.client, "get", return_value=[]) as mock_get:
            self.client.get_metars(["KJFK", "KLAX", "KORD"])
            call_params = mock_get.call_args[1]["params"]
            assert call_params["ids"] == "KJFK,KLAX,KORD"

    def test_get_metars_empty_response(self):
        """Empty API response returns empty list without crashing."""
        with patch.object(self.client, "get", return_value=[]):
            result = self.client.get_metars(["KJFK"])
            assert result == []

    def test_get_metars_custom_hours(self):
        """Custom hours parameter is passed correctly."""
        with patch.object(self.client, "get", return_value=[]) as mock_get:
            self.client.get_metars(["KJFK"], hours=6)
            call_params = mock_get.call_args[1]["params"]
            assert call_params["hours"] == 6

    def test_get_tafs_returns_list(self):
        """get_tafs returns list of TAF dicts."""
        with patch.object(self.client, "get", return_value=[MOCK_TAF]):
            result = self.client.get_tafs(["KJFK"])
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["icaoId"] == "KJFK"

    def test_get_tafs_passes_correct_params(self):
        """get_tafs calls the correct endpoint with correct params."""
        with patch.object(self.client, "get", return_value=[MOCK_TAF]) as mock_get:
            self.client.get_tafs(["KJFK", "KLAX"])
            mock_get.assert_called_once_with(
                "taf",
                params={
                    "ids": "KJFK,KLAX",
                    "format": "json",
                },
            )

    def test_get_tafs_empty_response(self):
        """Empty TAF response returns empty list without crashing."""
        with patch.object(self.client, "get", return_value=[]):
            result = self.client.get_tafs(["KJFK"])
            assert result == []


class TestGetAirportsFromEnv:

    def test_returns_default_when_env_not_set(self):
        """Returns DEFAULT_AIRPORTS when SKYLAKE_AIRPORTS is not set."""
        with patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("SKYLAKE_AIRPORTS", None)
            result = get_airports_from_env()
            assert result == DEFAULT_AIRPORTS

    def test_reads_airports_from_env(self):
        """Returns airports from SKYLAKE_AIRPORTS env var."""
        with patch.dict("os.environ", {"SKYLAKE_AIRPORTS": "KJFK,KLAX,KORD"}):
            result = get_airports_from_env()
            assert result == ["KJFK", "KLAX", "KORD"]

    def test_strips_whitespace_from_env(self):
        """Strips whitespace from airport codes in env var."""
        with patch.dict("os.environ", {"SKYLAKE_AIRPORTS": " KJFK , KLAX "}):
            result = get_airports_from_env()
            assert result == ["KJFK", "KLAX"]

    def test_uppercases_airport_codes(self):
        """Airport codes are uppercased regardless of input."""
        with patch.dict("os.environ", {"SKYLAKE_AIRPORTS": "kjfk,klax"}):
            result = get_airports_from_env()
            assert result == ["KJFK", "KLAX"]
