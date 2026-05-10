# Business Rules

All validation, constraints, and guards enforced across three layers, grouped by entity.

**Layer legend:**
- **PYD** — Pydantic v2 validator at build time. Pydantic IS the schema validator; `bundle.json` is its output. Violations abort the build.
- **JS** — Frontend guard (Svelte component or store action). Runs at runtime when importing wheel-state JSON or mutating wheel state.
- **UI** — Template-level rendering rule (e.g., plain-text-only for user content). Applied wherever the value is displayed in the DOM.

> This file is the **schema authority** for the project. [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md), [WORKFLOWS.md](WORKFLOWS.md), and `CLAUDE.md` reference this file for field-level details rather than redefining them.

---

## 1. Scent

Central domain record. Lives in `data/source/scents.json`. Every wheel display is driven by Scent records.

### Identity

| Rule | Layer | Enforcement |
|---|---|---|
| `id` is required | PYD | `Field(...)` — no default; missing field raises `ValidationError` |
| `id` must match kebab-case slug regex | PYD | `field_validator` applies `^[a-z0-9]+(-[a-z0-9]+)*$`; see [§7](#7-cross-cutting) |
| `id` must be unique across all Scent records | PYD | Cross-record validator in `load.py` checks for duplicates after bulk parse |
| `name` is required | PYD | `Field(...)` — non-empty string |

### Required Fields

| Rule | Layer | Enforcement |
|---|---|---|
| `domain` is required | PYD | `Literal["scent", "texture"]` — any other value raises `ValidationError` |
| `deprecated` is required | PYD | `bool` with `default=False`; field must be explicitly present in JSON |
| `category_ids` is required | PYD | `list[str]`, minimum length 1 — a Scent must belong to at least one Category |
| `compounds` may be empty list | PYD | `list[str]`, default `[]` — empty state is valid (no compounds recorded yet) |
| `synonyms` may be empty list | PYD | `list[str]`, default `[]` |
| `literature` may be empty list | PYD | `list[str]`, default `[]` |
| `sensory_anchors` may be empty list | PYD | `list[SensoryAnchor]`, default `[]` |
| `definition` is optional | PYD | `str \| None`, default `None` — user-authored; may be absent |
| `default_color` is optional | PYD | `str \| None`, default `None`; when present, must pass hex format check; see [§7](#7-cross-cutting) |

### Sensory Anchor Shape

Each item in `sensory_anchors` is a structured sub-object.

| Rule | Layer | Enforcement |
|---|---|---|
| `name` is required on each anchor | PYD | `Field(...)` — non-empty string |
| `modality` is required on each anchor | PYD | `Literal["aroma", "flavor"]` — any other value raises `ValidationError` |
| `preparation_notes` is optional | PYD | `str \| None`, default `None` |
| Anchor `name` renders as plain text only | UI | No `{@html}`, no Markdown; see [§7](#7-cross-cutting) |

### Referential Integrity

| Rule | Layer | Enforcement |
|---|---|---|
| Each `category_ids` entry must resolve to an existing Category `id` | PYD | Cross-entity validator in `load.py` checks after all entities are parsed |
| Each `compounds` entry must resolve to an existing Compound `id` | PYD | Cross-entity validator in `load.py` |
| Each `literature` entry must resolve to an existing Citation `id` | PYD | Cross-entity validator in `load.py` |
| Unresolvable foreign ID → build fails with descriptive error | PYD | Validator raises `ValueError` naming the missing ID and the owning Scent |
| Deprecated Category/Compound/Citation referenced by a Scent → warning only, not error | PYD | Validator emits `warnings.warn()` listing deprecated refs; build continues |

### Soft-Delete

| Rule | Layer | Enforcement |
|---|---|---|
| `deprecated: true` means record is excluded from wheel rendering | JS | `data.js` filters scents where `deprecated === true` before building Plotly figure |
| Deprecated Scent referenced in an imported wheel state → non-blocking warning | JS | Import validator collects deprecated references and surfaces them to the user |
| Deprecated records remain in `bundle.json` | PYD | Validator does not remove deprecated records; they are passed through |
| Hard deletion of Scent records is prohibited | PYD | Convention enforced by code review; `load.py` warns if a previously-seen `id` disappears |

---

## 2. Ingredient

Lives in `data/source/ingredients.json`. Role (base or target) is **per-wheel**, not per-record.

### Identity

| Rule | Layer | Enforcement |
|---|---|---|
| `id` is required | PYD | `Field(...)` |
| `id` must match kebab-case slug regex | PYD | Same `field_validator` as Scent; see [§7](#7-cross-cutting) |
| `id` must be unique across all Ingredient records | PYD | Cross-record duplicate check in `load.py` |
| `name` is required | PYD | `Field(...)` — non-empty string |

### Required Fields

| Rule | Layer | Enforcement |
|---|---|---|
| `deprecated` is required | PYD | `bool`, default `false` |
| `scents` may be empty list | PYD | `list[str]`, default `[]` — valid (ingredient has no scents recorded yet) |
| No `kind` / `role` field on this record | PYD | Model has no such field; presence would raise `ValidationError` (extra fields forbidden) |

### Referential Integrity

| Rule | Layer | Enforcement |
|---|---|---|
| Each `scents` entry must resolve to an existing Scent `id` | PYD | Cross-entity validator in `load.py` |
| Deprecated Scent referenced in an Ingredient → warning only | PYD | Same pattern as Scent; `warnings.warn()` |
| Unresolvable scent ID → build fails with descriptive error | PYD | `ValueError` naming the missing ID and owning Ingredient |

### Soft-Delete

| Rule | Layer | Enforcement |
|---|---|---|
| Deprecated Ingredient is hidden from the ingredient picker | JS | `data.js` filters on `deprecated` before populating the picker |
| Deprecated Ingredient referenced in an imported wheel state → non-blocking warning | JS | Same import-warning pattern as Scent |
| Hard deletion prohibited | PYD | Convention; `load.py` warns if a previously-seen `id` disappears |

---

## 3. Compound

Lives in `data/source/compounds.json`. The slug `id` is the universal canonical key inside the app; PubChem `cid` is authoritative external reference but optional.

### Identity

| Rule | Layer | Enforcement |
|---|---|---|
| `id` is required | PYD | `Field(...)` |
| `id` must match kebab-case slug regex | PYD | Same `field_validator`; see [§7](#7-cross-cutting) |
| `id` must be unique across all Compound records | PYD | Cross-record duplicate check in `load.py` |
| `name` is required | PYD | `Field(...)` — non-empty string |

### Required Fields

| Rule | Layer | Enforcement |
|---|---|---|
| `deprecated` is required | PYD | `bool`, default `false` |
| `synonyms` may be empty list | PYD | `list[str]`, default `[]` |
| `cid` is optional | PYD | `int \| None`, default `None` — some niche compounds lack a PubChem CID |
| `cas_number` is optional | PYD | `str \| None`, default `None`; when present, format enforced (see below) |
| `smiles` is optional | PYD | `str \| None`, default `None` |
| `formula` is optional | PYD | `str \| None`, default `None` |
| `flavordb_url` is optional | PYD | `str \| None`, default `None` |

### CID Uniqueness

| Rule | Layer | Enforcement |
|---|---|---|
| `cid`, when present, must be unique across all Compound records | PYD | Cross-record validator in `load.py` collects all non-null CIDs and checks for duplicates |
| Duplicate `cid` → build fails with descriptive error | PYD | `ValueError` naming both conflicting Compound slugs |

### CAS Number Format

| Rule | Layer | Enforcement |
|---|---|---|
| `cas_number`, when present, must match `^\d+-\d+-\d$` | PYD | `field_validator` applies regex; raises `ValidationError` on mismatch |

### Derived Fields (Not Stored)

| Rule | Layer | Enforcement |
|---|---|---|
| `pubchem_url` is **not** stored in JSON | PYD | Model has no `pubchem_url` field; derived at runtime as `https://pubchem.ncbi.nlm.nih.gov/compound/<cid>` |
| Derived URL is only generated when `cid` is non-null | JS | `data.js` / `SidePanel.svelte` gates the PubChem link on `cid != null` |

### Soft-Delete

| Rule | Layer | Enforcement |
|---|---|---|
| Deprecated Compound is hidden from side-panel compound list | JS | `SidePanel.svelte` filters compounds on `deprecated` |
| Hard deletion prohibited | PYD | Convention; same warn-on-disappearance pattern |

---

## 4. Citation

Lives in `data/source/citations.json`. Corresponds to papers in `Literature/`.

### Identity

| Rule | Layer | Enforcement |
|---|---|---|
| `id` is required | PYD | `Field(...)` |
| `id` must match kebab-case slug regex | PYD | Same `field_validator`; see [§7](#7-cross-cutting) |
| `id` must be unique across all Citation records | PYD | Cross-record duplicate check in `load.py` |

### Required Fields

| Rule | Layer | Enforcement |
|---|---|---|
| `title` is required | PYD | `Field(...)` — non-empty string |
| `authors` is required | PYD | `list[str]`, minimum length 1 |
| `year` is required | PYD | `int` — four-digit year; no upper/lower bound enforced |
| `source_kind` is required | PYD | `Literal["journal", "book_chapter", "review", "report"]` |
| `deprecated` is required | PYD | `bool`, default `false` |

### DOI / URL Constraint

| Rule | Layer | Enforcement |
|---|---|---|
| At least one of `doi` or `url` must be present | PYD | `model_validator(mode="after")` raises `ValueError` if both are `None` |
| `doi` is optional individually | PYD | `str \| None`, default `None` |
| `url` is optional individually | PYD | `str \| None`, default `None` |

### Optional Bibliographic Fields

| Rule | Layer | Enforcement |
|---|---|---|
| `journal` is optional | PYD | `str \| None`, default `None` |
| `volume` is optional | PYD | `str \| None`, default `None` |
| `pages` is optional | PYD | `str \| None`, default `None` |
| `publisher` is optional | PYD | `str \| None`, default `None` |

### Local PDF Integrity

| Rule | Layer | Enforcement |
|---|---|---|
| `local_pdf_filename` is optional | PYD | `str \| None`, default `None` |
| When present, file must exist at `Literature/<local_pdf_filename>` | PYD | `field_validator` calls `Path("Literature") / value` and checks `.exists()`; raises `ValueError` if missing |
| `local_pdf_filename` stores the bare filename only (no path prefix) | PYD | Validator rejects values containing `/` or `\` |

### Soft-Delete

| Rule | Layer | Enforcement |
|---|---|---|
| Deprecated Citation is hidden from the side-panel literature list | JS | `SidePanel.svelte` filters on `deprecated` |
| Hard deletion prohibited | PYD | Same convention |

---

## 5. Category

Lives in `data/source/taxonomy.json`. Forms a parent-pointer tree. Top-level taxonomy nodes are: Floral, Fruity, Vegetal, Roasted, Spicy, Animal, Mineral, Off-notes.

### Identity

| Rule | Layer | Enforcement |
|---|---|---|
| `id` is required | PYD | `Field(...)` |
| `id` must match kebab-case slug regex | PYD | Same `field_validator`; see [§7](#7-cross-cutting) |
| `id` must be unique across all Category records | PYD | Cross-record duplicate check in `load.py` |
| `name` is required | PYD | `Field(...)` — non-empty string |

### Required Fields

| Rule | Layer | Enforcement |
|---|---|---|
| `deprecated` is required | PYD | `bool`, default `false` |
| `parent_id` is required (may be null) | PYD | `str \| None` — null means top-level node |
| `default_color` is optional | PYD | `str \| None`, default `None`; when present, must pass hex format check; see [§7](#7-cross-cutting) |

### Referential Integrity

| Rule | Layer | Enforcement |
|---|---|---|
| `parent_id`, when non-null, must resolve to an existing Category `id` | PYD | Cross-entity validator in `load.py` |
| Self-reference (`parent_id == id`) is forbidden | PYD | Validator checks `parent_id != id`; raises `ValueError` on self-loop |
| Circular parent chains are forbidden | PYD | `load.py` walks the parent chain and raises `ValueError` if a cycle is detected |
| Unresolvable `parent_id` → build fails | PYD | `ValueError` naming the missing parent ID and owning Category |

### Soft-Delete

| Rule | Layer | Enforcement |
|---|---|---|
| Deprecated Category is excluded from the wheel taxonomy rendering | JS | `data.js` prunes deprecated categories when building the wheel tree |
| Deprecated Category still resolves for backward compatibility in imported wheel states | JS | Import validator warns but does not reject |
| Hard deletion prohibited | PYD | Convention |

---

## 6. Wheel State

The export / import / `localStorage` shape. Not a curated-data file — this is the live user session object. Schema version must match exactly.

### Top-Level Fields

| Rule | Layer | Enforcement |
|---|---|---|
| `schema_version` is required | JS | Type guard checks presence before any state mutation |
| `schema_version` must equal `1` exactly | JS | `if (state.schema_version !== 1) throw Error(...)` — fail loudly with expected vs. actual; see [§7](#7-cross-cutting) |
| `app_version` is required | JS | Type guard checks presence; non-empty string |
| `name` is required | JS | Non-empty string |
| `description` is optional | JS | `string \| undefined` |
| `author` is optional | JS | `string \| undefined` |
| `created_at` is required | JS | ISO-8601 datetime string |
| `updated_at` is required | JS | ISO-8601 datetime string; updated on every store mutation |

### Ingredients Array

| Rule | Layer | Enforcement |
|---|---|---|
| `ingredients` is required | JS | `list`, may be empty |
| Each entry must have `ingredient_id` | JS | Type guard |
| Each entry must have `role: "base" \| "target"` | JS | `if (!["base","target"].includes(entry.role)) throw Error(...)` |
| Each `ingredient_id` must resolve in `bundle.json` | JS | `data.js` lookup; unresolvable ID → non-blocking warning |
| Deprecated Ingredient in `ingredients` → warning on import | JS | Import validator |

### Scents Displayed

| Rule | Layer | Enforcement |
|---|---|---|
| `scents_displayed` is required | JS | `list[str]`, may be empty |
| Each entry must resolve to a Scent `id` in `bundle.json` | JS | Import validator; unresolvable entry → warning + skipped |
| Deprecated Scent in `scents_displayed` → warning on import | JS | Import validator |

### Custom Scents

| Rule | Layer | Enforcement |
|---|---|---|
| `custom_scents` is required | JS | `list`, may be empty |
| Each entry must have `name` | JS | Non-empty string; type guard |
| Each `category_ids` entry in a custom scent must resolve in `bundle.json` | JS | Import validator; non-blocking warning on miss |
| `definition` on a custom scent is optional | JS | `string \| undefined` |
| Custom scents are **scoped to this wheel only** — they do NOT enter the global library | JS | `data.js` keeps custom scents in a separate collection; never merged into the bundle |
| Custom scent `name` renders as plain text only | UI | No `{@html}`; see [§7](#7-cross-cutting) |

### Color Overrides

| Rule | Layer | Enforcement |
|---|---|---|
| `color_overrides` is required | JS | Object (map), may be empty `{}` |
| Keys are Scent `id` strings | JS | Type guard |
| Values must be valid hex color strings | JS | `^#[0-9a-fA-F]{6}$` check on import; invalid values are discarded with a warning |
| Color resolution precedence: per-scent override → `Scent.default_color` → Category `default_color` | JS | `wheel.js` resolves in this priority order |

### Display Settings

| Rule | Layer | Enforcement |
|---|---|---|
| `hierarchy_depth` is required | JS | Positive integer (`>= 1`) |
| `definitions_visible` is required | JS | `boolean` |
| `annotations` is required | JS | Object (map), may be empty `{}` |
| Annotation values render as plain text only | UI | No `{@html}`; see [§7](#7-cross-cutting) |

### Storage

| Rule | Layer | Enforcement |
|---|---|---|
| Total wheel-state JSON serialized size must not exceed ~1 MB | JS | `store.js` checks `JSON.stringify(state).length` before `localStorage.setItem()`; if exceeded, user is prompted to export and clear |
| On `localStorage` unavailable or quota error → degrade gracefully | JS | `try/catch` around `setItem()`; banner informs user auto-save is off; app continues in-memory |
| Import: file must parse as valid JSON before any state mutation | JS | `JSON.parse()` in `try/catch`; parse failure → user-facing error, state unchanged |
| Import: type guard runs before store update | JS | Structural validation before `store.set()`; invalid shape → user-facing error |

---

## 7. Cross-Cutting

Rules that apply to multiple entities. They are defined here **once** and referenced (not restated) in per-entity sections above.

### Kebab-Case Slug Regex

| Rule | Layer | Enforcement |
|---|---|---|
| All entity `id` fields must match `^[a-z0-9]+(-[a-z0-9]+)*$` | PYD | Shared `field_validator` applied to `id` on Scent, Ingredient, Compound, Citation, Category |
| Slug must be lowercase only (no uppercase) | PYD | Covered by the regex above |
| Slug must not start or end with a hyphen | PYD | Covered by the regex above |
| Slug must not contain consecutive hyphens | PYD | Covered by the regex above |
| IDs are stable; renames require an explicit migration | PYD | Convention; no automated rename support in v1 |

### Schema Version

| Rule | Layer | Enforcement |
|---|---|---|
| Every JSON file starts with `"schema_version": 1` | PYD / JS | PYD enforces on curated source files at build time; JS enforces on wheel-state imports at runtime |
| Schema version mismatch → fail loudly; do not silently upgrade | JS | `throw Error("schema_version mismatch: expected 1, got <actual>")` |
| `schema_version` is `int` type, not string | PYD / JS | Both layers validate type strictly |

### Hex Color Format

| Rule | Layer | Enforcement |
|---|---|---|
| All color fields (`default_color` on Scent / Category; `color_overrides` values on Wheel State) must match `^#[0-9a-fA-F]{6}$` | PYD | Shared `field_validator` on all color fields in Pydantic models |
| Invalid hex in wheel-state `color_overrides` → discard the entry, emit a warning | JS | Import validator; does not abort the import |
| Shorthand hex (`#abc`) is not accepted | PYD / JS | Both regex checks require exactly 6 hex digits |

### Soft-Delete Semantics

| Rule | Layer | Enforcement |
|---|---|---|
| Every entity record carries `deprecated: bool` | PYD | Required field on all five curated entity models |
| Deprecated records remain in `data/source/*.json` and `bundle.json` — files never shrink | PYD | Convention; hard deletion is prohibited |
| Past wheel exports keep resolving deprecated references | JS | Import validator warns but does not reject deprecated refs |
| App warns the user when an imported wheel state references a deprecated entity | JS | Import validator collects all deprecated refs and surfaces a single non-blocking warning message |
| Active records must never reference a deprecated record without a warning | PYD | Cross-entity validator emits `warnings.warn()` for each such reference |

### Plain-Text Rendering Rule

The following fields contain user-authored or externally-sourced content and **must render as plain text only** — no `{@html}`, no Markdown rendering, no `innerHTML` assignment. This eliminates the XSS surface from imported wheel-state JSON files.

| Field | Entity | Layer |
|---|---|---|
| `definition` | Scent | UI |
| `name` (custom scents) | Wheel State — `custom_scents` | UI |
| `definition` (custom scents) | Wheel State — `custom_scents` | UI |
| `annotations` values | Wheel State | UI |
| `sensory_anchors[].name` | Scent | UI |
| `sensory_anchors[].preparation_notes` | Scent | UI |
| `title` | Citation | UI |
| `name` | Wheel State top-level | UI |
| `description` | Wheel State top-level | UI |
| `author` | Wheel State top-level | UI |

**Enforcement:** All Svelte templates must use `{value}` text interpolation, never `{@html value}`. This rule is enforced by code review and (when tests exist) by a linting rule that flags `{@html}` in component files that receive user content.

---

*This file was created during the docs-first phase (2026-05-10). It is the single schema authority; update it when any field shape changes.*
