"""Serialize a validated `SourceBundle` into the frontend-facing `bundle.json`."""

from __future__ import annotations

import json
from pathlib import Path

from sensory_wheel.schemas import SourceBundle


def write_bundle(bundle: SourceBundle, output: Path, *, app_version: str) -> None:
    """Write a `bundle.json` containing the validated source bundle plus `app_version`.

    The frontend reads this file at runtime — see `frontend/src/lib/data.js`.
    """
    payload = bundle.model_dump(mode="json")
    payload["app_version"] = app_version
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
