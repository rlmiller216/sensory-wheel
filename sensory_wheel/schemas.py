"""Pydantic v2 models for the Sensory Wheel curated data layer.

Mirrors `docs/BUSINESS_RULES.md` field-for-field. Every PYD-layer rule
in BUSINESS_RULES has a corresponding constraint here; if these drift,
BUSINESS_RULES.md is the authority and this file must be brought back
into alignment.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

# ---------------------------------------------------------------------------
# §7 cross-cutting: kebab-case slug regex
# ---------------------------------------------------------------------------

KEBAB_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _validate_kebab_slug(value: str) -> str:
    if not KEBAB_SLUG_PATTERN.fullmatch(value):
        raise ValueError(
            f"invalid kebab-case slug: {value!r} (must match {KEBAB_SLUG_PATTERN.pattern})"
        )
    return value


KebabSlug = Annotated[str, AfterValidator(_validate_kebab_slug)]

# ---------------------------------------------------------------------------
# §7 cross-cutting: hex color format  ^#[0-9a-fA-F]{6}$
# ---------------------------------------------------------------------------

HexColor = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]

# ---------------------------------------------------------------------------
# Shared base model
# ---------------------------------------------------------------------------

SCHEMA_VERSION = 1


class _StrictBase(BaseModel):
    """All schema models forbid extra fields and freeze on construction."""

    model_config = ConfigDict(extra="forbid", frozen=True)


# ---------------------------------------------------------------------------
# §5  Category
# ---------------------------------------------------------------------------


class Category(_StrictBase):
    """A node in the aroma taxonomy. See BUSINESS_RULES.md §5."""

    id: KebabSlug
    name: str = Field(min_length=1)
    # Required-but-nullable per BUSINESS_RULES.md §5: callers must pass
    # parent_id explicitly (use None for top-level categories). The
    # `Field(...)` makes it required even though the type allows None.
    parent_id: KebabSlug | None = Field(...)
    default_color: HexColor | None = None
    deprecated: bool = False


# ---------------------------------------------------------------------------
# §3  Compound
# ---------------------------------------------------------------------------


class Compound(_StrictBase):
    """A chemical compound. See BUSINESS_RULES.md §3.

    `id` is the canonical key inside the app (kebab-slug). `cid` (PubChem
    Compound ID) is preferred but optional — some niche compounds lack one.
    `pubchem_url` is NOT stored; derive at render time from `cid`.
    """

    id: KebabSlug
    name: str = Field(min_length=1)
    cid: int | None = Field(default=None, ge=1)
    synonyms: list[str] = Field(default_factory=list)
    # CAS regex per BUSINESS_RULES.md §3 "CAS Number Format": digits-digits-digit.
    # No upper bound on group sizes — keep it loose to match the schema authority.
    cas_number: str | None = Field(default=None, pattern=r"^\d+-\d+-\d$")
    smiles: str | None = None
    formula: str | None = None
    flavordb_url: str | None = None
    deprecated: bool = False


# ---------------------------------------------------------------------------
# §4  Citation
# ---------------------------------------------------------------------------


class Citation(_StrictBase):
    """A literature reference. See BUSINESS_RULES.md §4."""

    id: KebabSlug
    title: str = Field(min_length=1)
    authors: list[str] = Field(min_length=1)
    # No range bounds per BUSINESS_RULES.md §4 — just int.
    year: int
    doi: str | None = None
    url: str | None = None
    journal: str | None = None
    volume: str | None = None
    pages: str | None = None
    publisher: str | None = None
    source_kind: Literal["journal", "book_chapter", "review", "report"]
    local_pdf_filename: str | None = None
    deprecated: bool = False

    @model_validator(mode="after")
    def _require_doi_or_url(self) -> Citation:
        if self.doi is None and self.url is None:
            raise ValueError("Citation must have at least one of `doi` or `url`")
        return self


# ---------------------------------------------------------------------------
# §1  SensoryAnchor + Scent
# ---------------------------------------------------------------------------


class SensoryAnchor(_StrictBase):
    """A real-world reference standard for a scent. See BUSINESS_RULES.md §1."""

    name: str = Field(min_length=1)
    modality: Literal["aroma", "flavor"]
    preparation_notes: str | None = None


class Scent(_StrictBase):
    """A descriptor / flavor / attribute. See BUSINESS_RULES.md §1."""

    id: KebabSlug
    name: str = Field(min_length=1)
    synonyms: list[str] = Field(default_factory=list)
    domain: Literal["scent", "texture"] = "scent"
    definition: str | None = None
    category_ids: list[KebabSlug] = Field(min_length=1)
    compounds: list[KebabSlug] = Field(default_factory=list)
    sensory_anchors: list[SensoryAnchor] = Field(default_factory=list)
    literature: list[KebabSlug] = Field(default_factory=list)
    default_color: HexColor | None = None
    deprecated: bool = False


# ---------------------------------------------------------------------------
# §2  Ingredient
# ---------------------------------------------------------------------------


class Ingredient(_StrictBase):
    """A base or target ingredient. See BUSINESS_RULES.md §2.

    Note: NO `kind: base | target` field. Role is per-wheel, chosen
    by the user when building a wheel — not stored here.
    """

    id: KebabSlug
    name: str = Field(min_length=1)
    scents: list[KebabSlug] = Field(default_factory=list)
    deprecated: bool = False


# ---------------------------------------------------------------------------
# Top-level SourceBundle
# ---------------------------------------------------------------------------


class SourceBundle(_StrictBase):
    """The full curated data set, validated as one unit.

    Loaded from `data/source/*.json` files. The bundle.json shape produced
    for the frontend is computed from this — see `sensory_wheel.bundle`.
    """

    schema_version: Literal[1] = SCHEMA_VERSION
    taxonomy: list[Category]
    scents: list[Scent]
    compounds: list[Compound]
    citations: list[Citation]
    ingredients: list[Ingredient]
