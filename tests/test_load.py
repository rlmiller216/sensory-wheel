"""Tests for sensory_wheel.load."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sensory_wheel.load import load_source_bundle


@pytest.fixture
def empty_source_dir(tmp_path: Path) -> Path:
    """A `data/source/` containing five empty-but-valid JSON files."""
    src = tmp_path / "source"
    src.mkdir()
    (src / "taxonomy.json").write_text(json.dumps({"schema_version": 1, "categories": []}))
    (src / "scents.json").write_text(json.dumps({"schema_version": 1, "scents": []}))
    (src / "compounds.json").write_text(json.dumps({"schema_version": 1, "compounds": []}))
    (src / "citations.json").write_text(json.dumps({"schema_version": 1, "citations": []}))
    (src / "ingredients.json").write_text(json.dumps({"schema_version": 1, "ingredients": []}))
    return src


class TestLoadSourceBundle:
    def test_loads_empty_bundle(self, empty_source_dir: Path):
        bundle = load_source_bundle(empty_source_dir)
        assert bundle.schema_version == 1
        assert bundle.taxonomy == []
        assert bundle.scents == []

    def test_rejects_missing_file(self, tmp_path: Path):
        empty = tmp_path / "source"
        empty.mkdir()
        # No files inside.
        with pytest.raises(FileNotFoundError):
            load_source_bundle(empty)

    def test_rejects_schema_version_mismatch(self, empty_source_dir: Path):
        bad = empty_source_dir / "taxonomy.json"
        bad.write_text(json.dumps({"schema_version": 2, "categories": []}))
        with pytest.raises(ValueError, match="schema_version"):
            load_source_bundle(empty_source_dir)

    def test_rejects_missing_list_key(self, empty_source_dir: Path):
        """A source file with the wrong list key (typo) should fail loudly."""
        bad = empty_source_dir / "taxonomy.json"
        bad.write_text(
            json.dumps({"schema_version": 1, "category": []})
        )  # typo: should be 'categories'
        with pytest.raises(ValueError, match="expected a top-level key"):
            load_source_bundle(empty_source_dir)

    def test_rejects_malformed_json(self, empty_source_dir: Path):
        """Malformed JSON in any source file should raise a contextualized ValueError."""
        bad = empty_source_dir / "taxonomy.json"
        bad.write_text("{ not valid json")
        with pytest.raises(ValueError, match="invalid JSON"):
            load_source_bundle(empty_source_dir)
