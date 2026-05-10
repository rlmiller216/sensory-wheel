# Sensory Wheel — System Architecture

> **Version**: 0.1.0
> **Date**: 2026-05-10
> **Status**: Living Document
> **Scope**: Static interactive sensory wheel app for plant-based-meat formulation

**Sources synthesized**: [2026-05-10-sensory-wheel-docs-design.md](./superpowers/specs/2026-05-10-sensory-wheel-docs-design.md) (design spec), prior `/init` plan captured in [CLAUDE.md](../CLAUDE.md), example markdown corpus from `lab-data-repo` SYSTEM_ARCHITECTURE.md

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Domain Model](#2-domain-model)
3. [Source Architecture](#3-source-architecture)
4. [Data Model](#4-data-model)
5. [Workflows](#5-workflows)
6. [Business Rules](#6-business-rules)
7. [Data Architecture](#7-data-architecture)
8. [Boundary Contracts](#8-boundary-contracts)
9. [Architectural Risks](#9-architectural-risks)
10. [Technical Debt & Known Gaps](#10-technical-debt--known-gaps)

---

## 1. System Overview

### 1.1 Single Bounded Context

The Sensory Wheel is a **single bounded context**: a public, static, interactive web application for plant-based-meat flavor formulation. There is no ERP integration, no multi-tenant logic, no server, and no database. The entire system consists of:

- A **Python build pipeline** that runs at deploy time to validate and bundle curated JSON data.
- A **Svelte 5 frontend** that runs entirely in the browser.
- **Netlify** as the static hosting target.

The app allows a user to select one or more **base** ingredients (e.g. pea protein) and one or more **target** ingredients (e.g. beef), then renders the union of all associated scents as a multi-layer sunburst chart organized by a curated aroma taxonomy. A side panel provides scent detail: definition, sensory anchors, compounds, and literature citations. Wheel state persists to `localStorage` and can be exported/imported as JSON.

### 1.2 Technology Stack

| Layer | Area | Decision |
|-------|------|----------|
| **Build time** | Curation language | Python 3.12+, managed by `uv` (Astral) |
| **Build time** | Schema validation | Pydantic v2 — validates `data/source/*.json` before bundling |
| **Build time** | Bundle output | `frontend/static/bundle.json` (gitignored; derived artifact) |
| **Runtime** | Frontend framework | Svelte 5 with Vite |
| **Runtime** | Visualization | Plotly.js `sunburst` (`plotly.js-strict-dist-min`, ~800 KB) |
| **Runtime** | In-browser PDF | jsPDF + html2canvas |
| **Runtime** | State management | Single Svelte `writable()` store, auto-synced to `localStorage` |
| **Runtime** | Export formats | SVG, PNG, PDF, JSON |
| **Deploy** | Hosting | Netlify (static) — no server, no cold starts |
| **Deploy** | Build command | `uv sync && uv run python scripts/build_bundle.py && cd frontend && npm install && npm run build` |
| **Deploy** | Publish directory | `frontend/dist/` |
| **Both** | Version control | Git, public GitHub repo, MIT license |

### 1.3 Codebase Summary

```
Sensory Wheel — 0 LOC, pre-implementation as of 2026-05-10
```

No source files exist yet. The project is in the docs-first phase. The `Literature/` folder is populated with 13 research PDFs; all other directories are planned but not yet created.

---

## 2. Domain Model

Six entities make up the curated data model. Role (base vs. target) is **not** an entity-level field — it is a per-wheel choice made by the user at runtime. For full field-level definitions and validation rules, see [BUSINESS_RULES.md](./BUSINESS_RULES.md).

### 2.1 Scent

The central domain record. A Scent represents a single flavor or aroma descriptor (e.g. "beany", "cut-grass", "meaty") associated with one or more ingredients, organized into the taxonomy via `category_ids`, and backed by compounds and citations. Every wheel display is driven by Scent records.

See [BUSINESS_RULES.md §1](./BUSINESS_RULES.md#1-scent) for full field definitions and validation rules.

### 2.2 Ingredient

Represents a curated plant-based or animal-protein ingredient (e.g. "pea-protein", "beef"). Carries a flat list of Scent IDs that are associated with this ingredient. Role assignment (base or target) is per-wheel and stored only in Wheel State, never on this record.

See [BUSINESS_RULES.md §2](./BUSINESS_RULES.md#2-ingredient) for full field definitions and validation rules.

### 2.3 Compound

A flavor-active molecule linked to one or more Scents (e.g. "hexanal", "2-acetyl-1-pyrroline"). The kebab-case slug `id` is the universal canonical key inside the app; PubChem `cid` is the preferred external reference but is optional for niche compounds. The `pubchem_url` is derived at runtime and not stored.

See [BUSINESS_RULES.md §3](./BUSINESS_RULES.md#3-compound) for full field definitions and validation rules.

### 2.4 Citation

A structured bibliographic reference corresponding to a paper in the `Literature/` folder or a source found via consensus.app. Requires at least one of `doi` or `url`. Referenced by Scent records via a list of Citation IDs.

See [BUSINESS_RULES.md §4](./BUSINESS_RULES.md#4-citation) for full field definitions and validation rules.

### 2.5 Category

A taxonomy node in the curated aroma classification tree. Organized as a parent-pointer tree (each node holds `parent_id`, not a children list). Top-level categories for v1 are: Floral, Fruity, Vegetal, Roasted, Spicy, Animal, Mineral, Off-notes. Categories may be nested (e.g. "Green" under "Vegetal").

See [BUSINESS_RULES.md §5](./BUSINESS_RULES.md#5-category) for full field definitions and validation rules.

### 2.6 Wheel State

The live user session object — not a curated-data file. Holds the current ingredient selection, displayed scents, custom (user-coined) scents, per-scent color overrides, hierarchy depth preference, annotation text, and visibility toggles. Auto-persisted to `localStorage`; exported/imported as JSON. `schema_version` must match exactly — mismatches are rejected loudly.

See [BUSINESS_RULES.md §6](./BUSINESS_RULES.md#6-wheel-state) for full field definitions and validation rules.

---

## 3. Source Architecture

> **Placeholder — to be populated after first scaffolding lands.**

This section will be expanded into (or replaced by) [SRC_ARCHITECTURE.md](./SRC_ARCHITECTURE.md) once the Python package and Svelte frontend are scaffolded. At that point it will document: the Python package structure (`sensory_wheel/`), module responsibilities, the Svelte component hierarchy, and the `data.js` / `store.js` / `wheel.js` frontend module contracts.

[SRC_ARCHITECTURE.md](./SRC_ARCHITECTURE.md) is explicitly deferred until code exists, per [the design spec](../superpowers/specs/2026-05-10-sensory-wheel-docs-design.md) §2: "SRC_ARCHITECTURE can't be written before code exists."

---

## 4. Data Model

### 4.1 JSON Record Shapes

These diagrams show the rough shape of each record type — enough to understand the structure at a glance. For complete field lists, types, defaults, and constraints, see [BUSINESS_RULES.md](./BUSINESS_RULES.md).

**Scent** (`data/source/scents.json`):
```jsonc
{
  "schema_version": 1,
  "scents": [
    {
      "id": "beany",
      "name": "Beany",
      "domain": "scent",
      "category_ids": ["vegetal"],
      "synonyms": ["bean-like", "pea-like"],
      "definition": "...",
      "sensory_anchors": [
        { "name": "...", "modality": "aroma", "preparation_notes": "..." }
      ],
      "compounds": ["hexanal", "2-pentylfuran"],
      "literature": ["maughan2012"],
      "default_color": null,
      "deprecated": false
    }
  ]
}
```

**Ingredient** (`data/source/ingredients.json`):
```jsonc
{
  "schema_version": 1,
  "ingredients": [
    {
      "id": "pea-protein",
      "name": "Pea Protein",
      "scents": ["beany", "earthy", "grassy"],
      "deprecated": false
    }
  ]
}
```

**Compound** (`data/source/compounds.json`):
```jsonc
{
  "schema_version": 1,
  "compounds": [
    {
      "id": "hexanal",
      "name": "Hexanal",
      "cid": 6752,
      // ... see BUSINESS_RULES.md §3 for full schema
      "deprecated": false
    }
  ]
}
```

**Citation** (`data/source/citations.json`):
```jsonc
{
  "schema_version": 1,
  "citations": [
    {
      "id": "maughan2012",
      "title": "...",
      "authors": ["Maughan, C.", "..."],
      "year": 2012,
      "doi": "10.xxxx/...",
      "url": null,
      "deprecated": false
    }
  ]
}
```

**Category** (`data/source/taxonomy.json`):
```jsonc
{
  "schema_version": 1,
  "categories": [
    { "id": "vegetal",  "name": "Vegetal",  "parent_id": null,    "default_color": null, "deprecated": false },
    { "id": "green",    "name": "Green",     "parent_id": "vegetal", "default_color": null, "deprecated": false }
  ]
}
```

**Wheel State** (`localStorage` / export JSON):
```jsonc
{
  "schema_version": 1,
  "app_version": "0.1.0",
  "name": "Pea-protein → beef formulation #3",
  "description": "...",
  "author": "Rebecca",
  "created_at": "2026-05-10T00:00:00Z",
  "updated_at": "2026-05-10T00:00:00Z",
  "ingredients": [
    { "ingredient_id": "pea-protein", "role": "base" },
    { "ingredient_id": "beef",        "role": "target" }
  ],
  "scents_displayed": ["beany", "meaty", "earthy"],
  "custom_scents": [
    { "name": "...", "category_ids": ["vegetal"], "definition": "..." }
  ],
  "color_overrides": { "beany": "#a4c639" },
  "hierarchy_depth": 3,
  "definitions_visible": false,
  "annotations": { "beany": "tried adding hexanal here, didn't work" }
}
```

### 4.2 Entity Relationship Diagram

Relationships between curated entities. All forward lists live in JSON files; reverse indexes are built in-memory at app startup by `load.py` (Python) and `data.js` (frontend). No junction files on disk.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CURATED DATA RELATIONSHIPS                        │
└─────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐          ┌──────────────┐
  │   Category   │◄─────────│    Scent     │
  │              │  M:N via │              │
  │  id          │ category_│  id          │
  │  name        │   ids[]  │  name        │
  │  parent_id ──┼──────┐   │  domain      │
  │  default_    │      │   │  category_   │
  │  color       │      │   │    ids[]     │
  │  deprecated  │      │   │  compounds[] │──────────┐
  └──────────────┘      │   │  literature[]│──────┐   │
        ▲               │   │  deprecated  │      │   │
        │ self-ref       │   └──────────────┘      │   │
        │ (parent-       │          ▲               │   │
        │  pointer)      │          │ M:N via       │   │
        └────────────────┘          │ scents[]      │   │
                                    │               │   │
                          ┌─────────┴────┐          │   │
                          │  Ingredient  │          │   │
                          │              │          │   │
                          │  id          │          │   │
                          │  name        │          │   │
                          │  scents[]    │          │   │
                          │  deprecated  │          │   │
                          └──────────────┘          │   │
                                                    │   │
                                          ┌─────────┴───┤
                                          │  Citation   │  ┌──────────────┐
                                          │             │  │   Compound   │
                                          │  id         │  │              │
                                          │  title      │  │  id          │
                                          │  authors[]  │  │  name        │
                                          │  year       │  │  cid         │
                                          │  doi / url  │  │  synonyms[]  │
                                          │  deprecated │  │  deprecated  │
                                          └─────────────┘  └──────────────┘

Cardinalities:
  Category ──< Category    (self-ref, parent-pointer; one parent, many children)
  Scent    >──< Category   (many-to-many via Scent.category_ids[])
  Scent    >──< Compound   (many-to-many via Scent.compounds[])
  Scent    >──< Citation   (many-to-many via Scent.literature[])
  Ingredient >──< Scent    (many-to-many via Ingredient.scents[])

Reverse indexes (runtime only, not on disk):
  scent_id      → list[ingredient_id]
  compound_id   → list[scent_id]
  category_id   → list[scent_id]
  category_id   → list[child_category_id]
```

---

## 5. Workflows

Full workflow documentation — curation pipeline, build pipeline, deploy pipeline, wheel-state lifecycle, PubChem fetcher, and testing workflow — lives in [WORKFLOWS.md](./WORKFLOWS.md).

---

## 6. Business Rules

All validation rules, field constraints, and enforcement layers (PYD / JS / UI) are defined in [BUSINESS_RULES.md](./BUSINESS_RULES.md). That file is the **schema authority** for the project. This document references it rather than redefining any field.

---

## 7. Data Architecture

### 7.1 Build-Time Pipeline

The deployed app contains no raw source data. Python runs at deploy time to validate and bundle the curated JSON into a single file consumed by the frontend.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        BUILD-TIME PIPELINE                            │
└──────────────────────────────────────────────────────────────────────┘

  data/source/                    Python (build time)
  ┌────────────────┐              ┌─────────────────────────────────────┐
  │ taxonomy.json  │──────────►  │  sensory_wheel/load.py              │
  │ scents.json    │             │  • Parse all source files            │
  │ compounds.json │             │  • Pydantic v2 model validation      │
  │ citations.json │             │  • Cross-entity referential checks   │
  │ ingredients.   │             │  • Build reverse indexes (in memory) │
  │   json         │             │  • Validate schema_version == 1      │
  └────────────────┘             └─────────────────┬───────────────────┘
                                                   │
                                                   ▼ BUILD FAILS if any
                                                     Pydantic error raised
                                                   │
                                                   ▼
                                  ┌────────────────────────────────────┐
                                  │  sensory_wheel/bundle.py           │
                                  │  • Serialize validated data +       │
                                  │    pre-built reverse indexes        │
                                  │  • Write bundle.json               │
                                  └────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                  frontend/static/bundle.json
                                  (gitignored — derived artifact)
                                                   │
                                                   ▼
                                  ┌────────────────────────────────────┐
                                  │  Vite build                        │
                                  │  cd frontend && npm run build      │
                                  │  • Bundles Svelte 5 app            │
                                  │  • Inlines / copies bundle.json    │
                                  │  • Tree-shakes Plotly.js           │
                                  └────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                  frontend/dist/
                                  (gitignored — Vite build output)
                                                   │
                                                   ▼
                                  ┌────────────────────────────────────┐
                                  │  Netlify deploy                    │
                                  │  • Publishes frontend/dist/        │
                                  │  • CDN edge distribution           │
                                  └────────────────────────────────────┘

Versioning note:
  VERSIONED  →  data/source/*.json   (truth; hand-edited by maintainer)
  DERIVED    →  frontend/static/bundle.json  (gitignored)
  DEPLOYED   →  frontend/dist/       (gitignored locally; Netlify serves)
```

### 7.2 Runtime Data Flow

```
  Browser startup
       │
       ▼
  fetch bundle.json (same-origin CDN)
       │
       ▼
  data.js: parse bundle → build runtime reverse indexes → expose lookups
       │
       ▼
  store.js: load wheel state from localStorage; validate schema_version == 1
       │
       ▼
  App renders ingredient picker → user picks base + target
       │
       ▼
  wheel.js: union scent IDs → resolve taxonomy → build Plotly sunburst spec
       │
       ▼
  Wheel.svelte: Plotly.js renders sunburst
       │
       ▼
  User interaction: pick, click wedge, export, annotate
       │
       ▼
  store.js: every mutation auto-saves to localStorage (~1 MB cap enforced)
```

---

## 8. Boundary Contracts

Three explicit contracts exist between system layers. Each contract defines what is exchanged, who validates it, and what fails if the contract is violated.

### 8.1 Python ↔ JavaScript: the `bundle.json` contract

| Dimension | Detail |
|-----------|--------|
| **What** | `frontend/static/bundle.json` — a single JSON file containing all validated curated records plus pre-built reverse indexes |
| **Version field** | `schema_version: 1` at the top level of bundle.json |
| **Who produces** | Python (`sensory_wheel/bundle.py`), invoked by `scripts/build_bundle.py` |
| **Who validates (write side)** | Pydantic v2 at build time — every entity record is validated before bundle.json is written |
| **Who consumes** | Frontend `data.js` at app startup |
| **Runtime validation** | None — the frontend trusts the bundle implicitly. No JSON Schema validator is shipped to the browser. |
| **If violated** | A malformed bundle.json (e.g., manually edited) will cause silent runtime failures or incorrect wheel renders. The only defense is not bypassing the Python build. |
| **Stability guarantee** | `schema_version` is bumped when the bundle shape changes incompatibly. Existing deployed builds will reject a mismatched bundle on next reload. |

### 8.2 Netlify Build Contract

| Dimension | Detail |
|-----------|--------|
| **What** | The Netlify build command defined in `netlify.toml` |
| **Command** | `uv sync && uv run python scripts/build_bundle.py && cd frontend && npm install && npm run build` |
| **Who enforces** | Netlify build environment executes the command verbatim |
| **Validation point** | `scripts/build_bundle.py` calls `load.py` which raises on any Pydantic `ValidationError`; a non-zero exit code aborts the Netlify deploy |
| **If violated** | If `build_bundle.py` exits non-zero (Pydantic failure, referential integrity error), the deploy fails and the previous successful deploy remains live (Netlify's atomic deploy guarantee) |
| **Implication** | Invalid `data/source/*.json` content cannot reach production. The Pydantic layer is the production gatekeeper. |

### 8.3 Browser localStorage Contract

| Dimension | Detail |
|-----------|--------|
| **What** | A single wheel-state JSON object persisted under a known `localStorage` key |
| **Key name** | `sensory_wheel_state` (provisional — confirmed in `store.js` at implementation time) |
| **Size cap** | ~1 MB per wheel. `store.js` checks `JSON.stringify(state).length` before each `setItem()` call |
| **Schema version** | `schema_version: 1` required. On mismatch (e.g., after a breaking schema change), the stored state is rejected and cleared; the user is prompted to start fresh or import a compatible export |
| **Who enforces** | `store.js` (write-side size check) and the import type guard in the JS layer (schema_version check on import) |
| **If violated** | Size overflow → user is prompted to export then clear. Schema mismatch → stored state is discarded; the user loses unsaved wheel state but the app continues working. `localStorage` unavailable → app degrades gracefully in-memory with a banner. |
| **Browser cap** | Raw browser `localStorage` quota is typically 5–10 MB. The ~1 MB per-wheel cap keeps well within this, leaving room for future multi-wheel support. |

---

## 9. Architectural Risks

Four concrete risks are identified for v1. Each has a specific mitigation already built into the spec.

### 9.1 — Bundle Size

**Risk**: As curated content grows beyond v1 targets (~100 scents, ~500 compounds, ~50 citations), `bundle.json` and the overall Vite bundle may grow to a size that causes perceptible first-load latency.

**Mitigation**:
- Netlify serves assets with gzip/brotli compression; JSON compresses well.
- Vite is configured to use the slim `plotly.js-strict-dist-min` build (~800 KB uncompressed, ~250 KB gzipped), not the full Plotly distribution.
- v1 data scale ceiling is explicitly capped (~100 scents, ~500 compounds). Exceeding it triggers a performance review before landing more content.

### 9.2 — localStorage 5–10 MB Browser Cap

**Risk**: Browser `localStorage` has a hard quota (typically 5–10 MB across all keys for a given origin). A user who creates many large wheels or who annotates heavily could hit this cap, causing `setItem()` to throw a `QuotaExceededError`.

**Mitigation**:
- The ~1 MB per-wheel cap enforced in `store.js` keeps each wheel well within budget.
- When the per-wheel cap is approached, the user is prompted to export the current wheel as JSON and clear `localStorage` before continuing.
- If `setItem()` throws despite the cap check (e.g., browser enforces a stricter global quota), the `try/catch` in `store.js` surfaces a banner: "Auto-save is off — export your wheel to preserve it."

### 9.3 — Plotly.js Sunburst Label Density

**Risk**: Plotly's sunburst implementation becomes visually unusable when there are more than ~50 leaf wedges — labels overlap, wedges become too narrow to click, and the chart degrades into an unreadable ring.

**Mitigation**:
- The hierarchy depth control (capability `#5-HD`) lets users collapse deeper scents into their parent's slice. This is the primary mitigation: a user can reduce visual density on demand.
- v1 data scale (5 bases × 5 targets) is unlikely to produce more than ~50 unique scents in a typical formulation wheel. Dense scenarios are expected only when a user adds many custom scents or selects all 10 ingredients simultaneously.
- For wheels that do approach this limit, the depth control defaults to 3 levels, which keeps most practical wheels readable.

### 9.4 — Content-Curation Throughput

**Risk**: Hand-curating structured JSON for 5 bases × 5 targets (scents + compounds + citations per ingredient) is time-intensive. Throughput bottleneck could delay the v1 success metric ("5×5 populated end-to-end").

**Mitigation**:
- The PubChem fetcher script (`scripts/fetch_compound.py`) automates the most tedious part of compound curation: given a CID, it calls PubChem PUG REST and produces a ready-to-paste Compound record (`name`, `synonyms`, `cas_number`, `smiles`, `formula`).
- consensus.app is the primary tool for synthesizing scent-attribute lists from the `Literature/` corpus without reading every paper manually.
- FlavorDB2 provides pre-linked ingredient → compound lists as a starting point for compound curation.

---

## 10. Technical Debt & Known Gaps

> **Pre-implementation as of 2026-05-10. No code has landed. This list is initially empty.**

As code lands, track deferred decisions here with a brief description and a linked capability code or commit reference. Typical entries: decisions made under time pressure during scaffolding, known edge-case gaps punted past v1, validation rules that are planned but not yet enforced.

---

*This file was created during the docs-first phase (2026-05-10). Update §3 (Source Architecture) and §10 (Technical Debt) as implementation progresses.*
