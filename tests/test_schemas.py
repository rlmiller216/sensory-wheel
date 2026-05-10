"""Tests for sensory_wheel.schemas Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from sensory_wheel.schemas import (
    Category,
    Citation,
    Compound,
    Ingredient,
    KebabSlug,
    Scent,
    SensoryAnchor,
    SourceBundle,
)

_slug_adapter = TypeAdapter(KebabSlug)


# ---------------------------------------------------------------------------
# KebabSlug
# ---------------------------------------------------------------------------


class TestKebabSlug:
    def test_accepts_valid_slug(self):
        assert _slug_adapter.validate_python("pea-protein") == "pea-protein"
        assert _slug_adapter.validate_python("beany") == "beany"
        assert _slug_adapter.validate_python("2-acetyl-1-pyrroline") == "2-acetyl-1-pyrroline"

    def test_rejects_uppercase(self):
        with pytest.raises(ValidationError):
            _slug_adapter.validate_python("Pea-Protein")

    def test_rejects_underscore(self):
        with pytest.raises(ValidationError):
            _slug_adapter.validate_python("pea_protein")

    def test_rejects_leading_hyphen(self):
        with pytest.raises(ValidationError):
            _slug_adapter.validate_python("-beany")

    def test_rejects_trailing_hyphen(self):
        with pytest.raises(ValidationError):
            _slug_adapter.validate_python("beany-")

    def test_rejects_empty(self):
        with pytest.raises(ValidationError):
            _slug_adapter.validate_python("")

    def test_rejects_consecutive_hyphens(self):
        with pytest.raises(ValidationError):
            _slug_adapter.validate_python("pea--protein")

    def test_accepts_numeric_segment(self):
        assert _slug_adapter.validate_python("c6h12") == "c6h12"

    def test_accepts_single_char(self):
        assert _slug_adapter.validate_python("a") == "a"


# ---------------------------------------------------------------------------
# Category  (§5)
# ---------------------------------------------------------------------------


class TestCategory:
    def test_accepts_top_level(self):
        c = Category(id="floral", name="Floral", parent_id=None)
        assert c.id == "floral"
        assert c.parent_id is None
        assert c.deprecated is False

    def test_accepts_with_parent_and_color(self):
        c = Category(
            id="green",
            name="Green",
            parent_id="vegetal",
            default_color="#88aa55",
        )
        assert c.parent_id == "vegetal"
        assert c.default_color == "#88aa55"

    def test_accepts_deprecated_true(self):
        c = Category(id="old-cat", name="Old", parent_id=None, deprecated=True)
        assert c.deprecated is True

    def test_rejects_missing_parent_id(self):
        # parent_id is required-but-nullable per BUSINESS_RULES.md §5.
        with pytest.raises(ValidationError):
            Category(id="floral", name="Floral")

    def test_rejects_invalid_id(self):
        with pytest.raises(ValidationError):
            Category(id="Floral", name="Floral", parent_id=None)

    def test_rejects_invalid_color(self):
        with pytest.raises(ValidationError):
            Category(id="floral", name="Floral", parent_id=None, default_color="not-a-hex")

    def test_rejects_shorthand_hex(self):
        # §7: shorthand #abc is not accepted — must be exactly 6 hex digits
        with pytest.raises(ValidationError):
            Category(id="floral", name="Floral", parent_id=None, default_color="#abc")

    def test_rejects_extra_field(self):
        with pytest.raises(ValidationError):
            Category(id="floral", name="Floral", parent_id=None, invented_field=123)

    def test_accepts_uppercase_hex(self):
        # §7 pattern allows A-F uppercase
        c = Category(id="floral", name="Floral", parent_id=None, default_color="#FF88AA")
        assert c.default_color == "#FF88AA"


# ---------------------------------------------------------------------------
# Compound  (§3)
# ---------------------------------------------------------------------------


class TestCompound:
    def test_accepts_minimal(self):
        c = Compound(id="hexanal", name="Hexanal")
        assert c.id == "hexanal"
        assert c.cid is None
        assert c.synonyms == []
        assert c.deprecated is False

    def test_accepts_optional_cid(self):
        c = Compound(id="hexanal", name="Hexanal", cid=6587)
        assert c.cid == 6587

    def test_rejects_cid_zero(self):
        with pytest.raises(ValidationError):
            Compound(id="hexanal", name="Hexanal", cid=0)

    def test_rejects_cid_negative(self):
        with pytest.raises(ValidationError):
            Compound(id="hexanal", name="Hexanal", cid=-1)

    def test_accepts_valid_cas(self):
        c = Compound(id="hexanal", name="Hexanal", cas_number="66-25-1")
        assert c.cas_number == "66-25-1"

    def test_accepts_longer_cas(self):
        c = Compound(id="some-compound", name="Some", cas_number="12345-67-8")
        assert c.cas_number == "12345-67-8"

    def test_rejects_invalid_cas_alpha(self):
        with pytest.raises(ValidationError):
            Compound(id="hexanal", name="Hexanal", cas_number="abc")

    def test_rejects_invalid_cas_format(self):
        # Must have exactly three digit groups separated by hyphens; last group exactly 1 digit
        with pytest.raises(ValidationError):
            Compound(id="hexanal", name="Hexanal", cas_number="12345678")

    def test_rejects_invalid_id(self):
        with pytest.raises(ValidationError):
            Compound(id="Hexanal", name="Hexanal")

    def test_rejects_extra_field(self):
        with pytest.raises(ValidationError):
            Compound(id="hexanal", name="Hexanal", invented_field="x")

    def test_synonyms_defaults_to_empty(self):
        c = Compound(id="hexanal", name="Hexanal")
        assert c.synonyms == []

    def test_accepts_synonyms(self):
        c = Compound(id="hexanal", name="Hexanal", synonyms=["n-Hexanal", "Caproaldehyde"])
        assert len(c.synonyms) == 2

    def test_rejects_pubchem_url_field(self):
        # pubchem_url must NOT be stored; model has no such field
        with pytest.raises(ValidationError):
            Compound(
                id="hexanal",
                name="Hexanal",
                pubchem_url="https://pubchem.ncbi.nlm.nih.gov/compound/6587",
            )


# ---------------------------------------------------------------------------
# Citation  (§4)
# ---------------------------------------------------------------------------

_CITATION_BASE = {
    "id": "doe-2021",
    "title": "Flavor Chemistry of Pea Protein",
    "authors": ["Doe, J.", "Smith, A."],
    "year": 2021,
    "source_kind": "journal",
}


class TestCitation:
    def test_accepts_doi_only(self):
        c = Citation(**_CITATION_BASE, doi="10.1234/example")
        assert c.doi == "10.1234/example"
        assert c.url is None

    def test_accepts_url_only(self):
        c = Citation(**_CITATION_BASE, url="https://example.com/paper")
        assert c.url == "https://example.com/paper"
        assert c.doi is None

    def test_accepts_both_doi_and_url(self):
        c = Citation(**_CITATION_BASE, doi="10.1234/example", url="https://example.com/paper")
        assert c.doi is not None
        assert c.url is not None

    def test_rejects_neither_doi_nor_url(self):
        with pytest.raises(ValidationError, match="doi.*url|url.*doi"):
            Citation(**_CITATION_BASE)

    def test_rejects_unknown_source_kind(self):
        data = {**_CITATION_BASE, "doi": "10.1234/x", "source_kind": "blogpost"}
        with pytest.raises(ValidationError):
            Citation(**data)

    def test_rejects_empty_authors(self):
        data = {**_CITATION_BASE, "authors": [], "doi": "10.1234/x"}
        with pytest.raises(ValidationError):
            Citation(**data)

    def test_accepts_all_source_kinds(self):
        for kind in ("journal", "book_chapter", "review", "report"):
            data = {**_CITATION_BASE, "doi": "10.1234/x", "source_kind": kind}
            c = Citation(**data)
            assert c.source_kind == kind

    def test_optional_fields_default_none(self):
        c = Citation(**_CITATION_BASE, doi="10.1234/x")
        assert c.journal is None
        assert c.volume is None
        assert c.pages is None
        assert c.publisher is None
        assert c.local_pdf_filename is None

    def test_deprecated_defaults_false(self):
        c = Citation(**_CITATION_BASE, doi="10.1234/x")
        assert c.deprecated is False

    def test_rejects_extra_field(self):
        with pytest.raises(ValidationError):
            Citation(**_CITATION_BASE, doi="10.1234/x", invented_field="x")

    def test_rejects_kebab_id_violation(self):
        data = {**_CITATION_BASE, "id": "Doe_2021", "doi": "10.1234/x"}
        with pytest.raises(ValidationError):
            Citation(**data)

    def test_accepts_local_pdf_filename_none(self):
        c = Citation(**_CITATION_BASE, doi="10.1234/x", local_pdf_filename=None)
        assert c.local_pdf_filename is None

    def test_accepts_local_pdf_filename_bare_string(self):
        """PYD layer accepts any bare string. File-existence check
        is deferred to a follow-up CD-hardening plan."""
        c = Citation(
            id="test-2024",
            title="A paper",
            authors=["Doe, J."],
            year=2024,
            doi="10.1234/test",
            source_kind="journal",
            local_pdf_filename="any-filename-even-nonexistent.pdf",
        )
        assert c.local_pdf_filename == "any-filename-even-nonexistent.pdf"

    def test_rejects_local_pdf_filename_with_path_separator(self):
        """Per BUSINESS_RULES.md §4: local_pdf_filename is a bare filename,
        no path prefix. (File-existence is deferred.)"""
        with pytest.raises(ValidationError):
            Citation(
                **{**_CITATION_BASE, "doi": "10.1234/x", "local_pdf_filename": "subdir/paper.pdf"},
            )
        with pytest.raises(ValidationError):
            Citation(
                **{**_CITATION_BASE, "doi": "10.1234/x", "local_pdf_filename": "..\\evil.pdf"},
            )

    def test_no_year_bounds(self):
        # BUSINESS_RULES.md §4: no upper/lower bound on year
        c1 = Citation(**{**_CITATION_BASE, "doi": "10.1234/x", "year": 1800})
        c2 = Citation(**{**_CITATION_BASE, "doi": "10.1234/x", "year": 2100})
        assert c1.year == 1800
        assert c2.year == 2100


# ---------------------------------------------------------------------------
# SensoryAnchor  (§1)
# ---------------------------------------------------------------------------


class TestSensoryAnchor:
    def test_accepts_aroma_modality(self):
        a = SensoryAnchor(name="Cut grass", modality="aroma")
        assert a.modality == "aroma"

    def test_accepts_flavor_modality(self):
        a = SensoryAnchor(name="Fresh pea taste", modality="flavor")
        assert a.modality == "flavor"

    def test_accepts_preparation_notes(self):
        a = SensoryAnchor(name="Smoke", modality="aroma", preparation_notes="Smoked on oak")
        assert a.preparation_notes == "Smoked on oak"

    def test_preparation_notes_defaults_none(self):
        a = SensoryAnchor(name="Vanilla", modality="aroma")
        assert a.preparation_notes is None

    def test_rejects_bogus_modality(self):
        with pytest.raises(ValidationError):
            SensoryAnchor(name="Something", modality="tactile")

    def test_rejects_empty_name(self):
        with pytest.raises(ValidationError):
            SensoryAnchor(name="", modality="aroma")

    def test_rejects_extra_field(self):
        with pytest.raises(ValidationError):
            SensoryAnchor(name="Vanilla", modality="aroma", intensity=5)


# ---------------------------------------------------------------------------
# Scent  (§1)
# ---------------------------------------------------------------------------


class TestScent:
    def test_accepts_minimal(self):
        s = Scent(id="beany", name="Beany", category_ids=["vegetal"])
        assert s.id == "beany"
        assert s.domain == "scent"
        assert s.synonyms == []
        assert s.compounds == []
        assert s.sensory_anchors == []
        assert s.literature == []
        assert s.deprecated is False

    def test_accepts_multi_category(self):
        s = Scent(id="earthy", name="Earthy", category_ids=["vegetal", "mineral"])
        assert s.category_ids == ["vegetal", "mineral"]

    def test_rejects_empty_category_ids(self):
        # BUSINESS_RULES.md §1: min length 1
        with pytest.raises(ValidationError):
            Scent(id="beany", name="Beany", category_ids=[])

    def test_rejects_missing_category_ids(self):
        with pytest.raises(ValidationError):
            Scent(id="beany", name="Beany")

    def test_rejects_invalid_hex_color(self):
        with pytest.raises(ValidationError):
            Scent(id="beany", name="Beany", category_ids=["vegetal"], default_color="red")

    def test_accepts_valid_hex_color(self):
        s = Scent(id="beany", name="Beany", category_ids=["vegetal"], default_color="#aabbcc")
        assert s.default_color == "#aabbcc"

    def test_accepts_sensory_anchor_aroma(self):
        anchor = SensoryAnchor(name="Soy milk", modality="aroma")
        s = Scent(id="beany", name="Beany", category_ids=["vegetal"], sensory_anchors=[anchor])
        assert s.sensory_anchors[0].modality == "aroma"

    def test_accepts_sensory_anchor_flavor(self):
        anchor = SensoryAnchor(name="Soy milk", modality="flavor")
        s = Scent(id="beany", name="Beany", category_ids=["vegetal"], sensory_anchors=[anchor])
        assert s.sensory_anchors[0].modality == "flavor"

    def test_default_domain_is_scent(self):
        s = Scent(id="beany", name="Beany", category_ids=["vegetal"])
        assert s.domain == "scent"

    def test_accepts_texture_domain(self):
        s = Scent(id="gritty", name="Gritty", category_ids=["texture"], domain="texture")
        assert s.domain == "texture"

    def test_rejects_invalid_domain(self):
        with pytest.raises(ValidationError):
            Scent(id="beany", name="Beany", category_ids=["vegetal"], domain="taste")

    def test_rejects_invalid_id(self):
        with pytest.raises(ValidationError):
            Scent(id="Beany", name="Beany", category_ids=["vegetal"])

    def test_rejects_extra_field(self):
        with pytest.raises(ValidationError):
            Scent(id="beany", name="Beany", category_ids=["vegetal"], invented_field=True)


# ---------------------------------------------------------------------------
# Ingredient  (§2)
# ---------------------------------------------------------------------------


class TestIngredient:
    def test_accepts_minimal(self):
        i = Ingredient(id="pea-protein", name="Pea Protein")
        assert i.id == "pea-protein"
        assert i.scents == []
        assert i.deprecated is False

    def test_accepts_empty_scents(self):
        # Stub ingredient with no scents is valid
        i = Ingredient(id="sunflower-oil", name="Sunflower Oil", scents=[])
        assert i.scents == []

    def test_accepts_scents_list(self):
        i = Ingredient(id="pea-protein", name="Pea Protein", scents=["beany", "grassy"])
        assert i.scents == ["beany", "grassy"]

    def test_rejects_invalid_id(self):
        with pytest.raises(ValidationError):
            Ingredient(id="PeaProtein", name="Pea Protein")

    def test_rejects_kind_field(self):
        # BUSINESS_RULES.md §2: no `kind` field; extra fields are forbidden
        with pytest.raises(ValidationError):
            Ingredient(id="pea-protein", name="Pea Protein", kind="base")

    def test_rejects_role_field(self):
        # Also test `role` for good measure
        with pytest.raises(ValidationError):
            Ingredient(id="pea-protein", name="Pea Protein", role="target")

    def test_rejects_extra_field(self):
        with pytest.raises(ValidationError):
            Ingredient(id="pea-protein", name="Pea Protein", invented_field="x")

    def test_deprecated_defaults_false(self):
        i = Ingredient(id="pea-protein", name="Pea Protein")
        assert i.deprecated is False


# ---------------------------------------------------------------------------
# SourceBundle
# ---------------------------------------------------------------------------


class TestSourceBundle:
    def test_accepts_empty_but_valid_bundle(self):
        b = SourceBundle(
            schema_version=1,
            taxonomy=[],
            scents=[],
            compounds=[],
            citations=[],
            ingredients=[],
        )
        assert b.schema_version == 1

    def test_rejects_schema_version_2(self):
        with pytest.raises(ValidationError):
            SourceBundle(
                schema_version=2,
                taxonomy=[],
                scents=[],
                compounds=[],
                citations=[],
                ingredients=[],
            )

    def test_rejects_schema_version_string(self):
        with pytest.raises(ValidationError):
            SourceBundle(
                schema_version="1",  # type: ignore[arg-type]
                taxonomy=[],
                scents=[],
                compounds=[],
                citations=[],
                ingredients=[],
            )

    def test_accepts_category_in_taxonomy(self):
        cat = Category(id="floral", name="Floral", parent_id=None)
        b = SourceBundle(
            schema_version=1,
            taxonomy=[cat],
            scents=[],
            compounds=[],
            citations=[],
            ingredients=[],
        )
        assert len(b.taxonomy) == 1

    def test_accepts_scent_in_scents(self):
        scent = Scent(id="beany", name="Beany", category_ids=["vegetal"])
        b = SourceBundle(
            schema_version=1,
            taxonomy=[],
            scents=[scent],
            compounds=[],
            citations=[],
            ingredients=[],
        )
        assert len(b.scents) == 1

    def test_accepts_compound_in_compounds(self):
        compound = Compound(id="hexanal", name="Hexanal")
        b = SourceBundle(
            schema_version=1,
            taxonomy=[],
            scents=[],
            compounds=[compound],
            citations=[],
            ingredients=[],
        )
        assert len(b.compounds) == 1

    def test_accepts_citation_in_citations(self):
        citation = Citation(
            id="doe-2021",
            title="Test Paper",
            authors=["Doe, J."],
            year=2021,
            source_kind="journal",
            doi="10.1234/x",
        )
        b = SourceBundle(
            schema_version=1,
            taxonomy=[],
            scents=[],
            compounds=[],
            citations=[citation],
            ingredients=[],
        )
        assert len(b.citations) == 1

    def test_accepts_ingredient_in_ingredients(self):
        ingredient = Ingredient(id="pea-protein", name="Pea Protein")
        b = SourceBundle(
            schema_version=1,
            taxonomy=[],
            scents=[],
            compounds=[],
            citations=[],
            ingredients=[ingredient],
        )
        assert len(b.ingredients) == 1

    def test_rejects_extra_field(self):
        with pytest.raises(ValidationError):
            SourceBundle(
                schema_version=1,
                taxonomy=[],
                scents=[],
                compounds=[],
                citations=[],
                ingredients=[],
                extra_stuff="not allowed",
            )
