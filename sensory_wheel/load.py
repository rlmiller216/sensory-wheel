"""Load + validate `data/source/*.json` into a `SourceBundle`."""

from __future__ import annotations

import json
from pathlib import Path

from sensory_wheel.schemas import SCHEMA_VERSION, SourceBundle

# Map of source filename → key inside that file that holds the list.
_SOURCE_FILES = {
    "taxonomy.json": "categories",
    "scents.json": "scents",
    "compounds.json": "compounds",
    "citations.json": "citations",
    "ingredients.json": "ingredients",
}

# Map of source filename → key in `SourceBundle` where the list belongs.
_BUNDLE_KEYS = {
    "taxonomy.json": "taxonomy",
    "scents.json": "scents",
    "compounds.json": "compounds",
    "citations.json": "citations",
    "ingredients.json": "ingredients",
}


def load_source_bundle(source_dir: Path) -> SourceBundle:
    """Load every `data/source/*.json` file, validate, return a bundle.

    Raises:
        FileNotFoundError: if any required source file is missing.
        ValueError: if any file has a wrong schema_version.
        pydantic.ValidationError: if any record fails Pydantic validation.
    """
    merged: dict[str, object] = {"schema_version": SCHEMA_VERSION}

    for filename, list_key in _SOURCE_FILES.items():
        path = source_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"required source file missing: {path}")

        raw = json.loads(path.read_text())
        if raw.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(
                f"{path}: schema_version is {raw.get('schema_version')!r}; "
                f"expected {SCHEMA_VERSION}"
            )

        merged[_BUNDLE_KEYS[filename]] = raw.get(list_key, [])

    return SourceBundle.model_validate(merged)
