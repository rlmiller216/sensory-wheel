"""Tests for sensory_wheel.bundle."""

from __future__ import annotations

import json
from pathlib import Path

from sensory_wheel.bundle import write_bundle
from sensory_wheel.schemas import SourceBundle


def test_write_bundle_produces_valid_json(tmp_path: Path):
    bundle = SourceBundle(
        taxonomy=[],
        scents=[],
        compounds=[],
        citations=[],
        ingredients=[],
    )
    out = tmp_path / "bundle.json"
    write_bundle(bundle, out, app_version="0.1.0")

    written = json.loads(out.read_text())
    assert written["schema_version"] == 1
    assert written["app_version"] == "0.1.0"
    assert written["taxonomy"] == []
    assert written["scents"] == []
