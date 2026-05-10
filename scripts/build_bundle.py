"""Build the frontend bundle from `data/source/*.json`.

Entry point for the Netlify build pipeline. See `netlify.toml`.

Usage:
    uv run python scripts/build_bundle.py

Reads from:  data/source/*.json
Writes to:   frontend/static/bundle.json
"""

from __future__ import annotations

import sys
from importlib.metadata import version
from pathlib import Path

from sensory_wheel.bundle import write_bundle
from sensory_wheel.load import load_source_bundle

# Hard-coded paths — this script runs from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "data" / "source"
OUTPUT = REPO_ROOT / "frontend" / "static" / "bundle.json"

# Read from pyproject.toml so the bundle's app_version always matches
# the installed package version. (To bump, edit `version` in pyproject.toml.)
APP_VERSION = version("sensory-wheel")


def main() -> int:
    print(f"Loading source from {SOURCE_DIR.relative_to(REPO_ROOT)}…")
    bundle = load_source_bundle(SOURCE_DIR)
    print(
        f"Validated: {len(bundle.taxonomy)} categories, {len(bundle.scents)} scents, "
        f"{len(bundle.compounds)} compounds, {len(bundle.citations)} citations, "
        f"{len(bundle.ingredients)} ingredients."
    )
    write_bundle(bundle, OUTPUT, app_version=APP_VERSION)
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} (app_version={APP_VERSION}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
