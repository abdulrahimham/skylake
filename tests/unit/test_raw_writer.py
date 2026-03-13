"""
Unit tests for ingestion/writers/raw_writer.py

Tests file naming, date partitioning, metadata embedding,
and file content using a temporary directory.
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path

from ingestion.writers.raw_writer import write_raw_metar, write_raw_taf


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_data_dir(tmp_path, monkeypatch):
    """Redirect raw writer to a temporary directory for testing."""
    monkeypatch.setattr("ingestion.writers.raw_writer.RAW_DIR", tmp_path / "raw")
    return tmp_path / "raw"


@pytest.fixture
def sample_metar():
    """A minimal but realistic METAR record."""
    return {
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


@pytest.fixture
def sample_taf():
    """A minimal but realistic TAF record."""
    return {
        "icaoId": "KJFK",
        "issueTime": "2026-03-12T22:26:00.000Z",
        "rawTAF": "TAF KJFK 122226Z 1224/1324 27015KT P6SM SCT030",
        "fcsts": [
            {"timeFrom": 1773352800, "timeTo": 1773360000, "wdir": 270, "wspd": 15}
        ],
    }


@pytest.fixture
def ingested_at():
    """Fixed ingestion timestamp for deterministic tests."""
    return datetime(2026, 3, 12, 23, 21, 28, tzinfo=timezone.utc)


# ── METAR writer tests ────────────────────────────────────────────────────────

class TestWriteRawMetar:

    def test_returns_list_of_paths(self, sample_metar, tmp_data_dir, ingested_at):
        """write_raw_metar returns a list of Path objects."""
        paths = write_raw_metar([sample_metar], ingested_at=ingested_at)
        assert isinstance(paths, list)
        assert len(paths) == 1
        assert isinstance(paths[0], Path)

    def test_file_exists_on_disk(self, sample_metar, tmp_data_dir, ingested_at):
        """Written file actually exists on disk."""
        paths = write_raw_metar([sample_metar], ingested_at=ingested_at)
        assert paths[0].exists()

    def test_date_partitioned_path(self, sample_metar, tmp_data_dir, ingested_at):
        """File is written to date-partitioned directory YYYY/MM/DD."""
        paths = write_raw_metar([sample_metar], ingested_at=ingested_at)
        path_str = str(paths[0])
        assert "2026" in path_str
        assert "03" in path_str
        assert "12" in path_str

    def test_filename_contains_airport_and_type(self, sample_metar, tmp_data_dir, ingested_at):
        """Filename contains data type and airport code."""
        paths = write_raw_metar([sample_metar], ingested_at=ingested_at)
        filename = paths[0].name
        assert "metar" in filename
        assert "KJFK" in filename

    def test_filename_is_json(self, sample_metar, tmp_data_dir, ingested_at):
        """File has .json extension."""
        paths = write_raw_metar([sample_metar], ingested_at=ingested_at)
        assert paths[0].suffix == ".json"

    def test_file_contains_original_data(self, sample_metar, tmp_data_dir, ingested_at):
        """Written file contains the original METAR fields."""
        paths = write_raw_metar([sample_metar], ingested_at=ingested_at)
        content = json.loads(paths[0].read_text())
        assert content["icaoId"] == "KJFK"
        assert content["temp"] == 1.1
        assert content["fltCat"] == "IFR"

    def test_file_contains_skylake_meta(self, sample_metar, tmp_data_dir, ingested_at):
        """Written file contains _skylake_meta block with lineage info."""
        paths = write_raw_metar([sample_metar], ingested_at=ingested_at)
        content = json.loads(paths[0].read_text())
        assert "_skylake_meta" in content
        assert content["_skylake_meta"]["source"] == "noaa_awc"
        assert content["_skylake_meta"]["data_type"] == "metar"
        assert "ingested_at" in content["_skylake_meta"]

    def test_multiple_records_write_multiple_files(self, sample_metar, tmp_data_dir, ingested_at):
        """Multiple records produce multiple files."""
        second_metar = {**sample_metar, "icaoId": "KLAX", "reportTime": "2026-03-12T22:00:00.000Z"}
        paths = write_raw_metar([sample_metar, second_metar], ingested_at=ingested_at)
        assert len(paths) == 2

    def test_empty_list_writes_no_files(self, tmp_data_dir, ingested_at):
        """Empty input list writes no files and returns empty list."""
        paths = write_raw_metar([], ingested_at=ingested_at)
        assert paths == []


# ── TAF writer tests ──────────────────────────────────────────────────────────

class TestWriteRawTaf:

    def test_returns_list_of_paths(self, sample_taf, tmp_data_dir, ingested_at):
        """write_raw_taf returns a list of Path objects."""
        paths = write_raw_taf([sample_taf], ingested_at=ingested_at)
        assert isinstance(paths, list)
        assert len(paths) == 1

    def test_file_exists_on_disk(self, sample_taf, tmp_data_dir, ingested_at):
        """Written TAF file actually exists on disk."""
        paths = write_raw_taf([sample_taf], ingested_at=ingested_at)
        assert paths[0].exists()

    def test_filename_contains_taf_and_airport(self, sample_taf, tmp_data_dir, ingested_at):
        """TAF filename contains data type and airport code."""
        paths = write_raw_taf([sample_taf], ingested_at=ingested_at)
        filename = paths[0].name
        assert "taf" in filename
        assert "KJFK" in filename

    def test_file_contains_skylake_meta(self, sample_taf, tmp_data_dir, ingested_at):
        """TAF file contains _skylake_meta with correct data_type."""
        paths = write_raw_taf([sample_taf], ingested_at=ingested_at)
        content = json.loads(paths[0].read_text())
        assert "_skylake_meta" in content
        assert content["_skylake_meta"]["data_type"] == "taf"

    def test_file_contains_original_data(self, sample_taf, tmp_data_dir, ingested_at):
        """Written TAF file contains original TAF fields."""
        paths = write_raw_taf([sample_taf], ingested_at=ingested_at)
        content = json.loads(paths[0].read_text())
        assert content["icaoId"] == "KJFK"
        assert "rawTAF" in content
