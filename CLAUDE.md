# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

**Pre-implementation as of 2026-05-10.** No `pyproject.toml`, no source files, no curated JSON yet. The `Literature/` folder is populated with 13 papers on meat / fish / poultry flavor chemistry and meat-analogue texture — this is the maintainer's research corpus, not app data.

This CLAUDE.md is a **seed** that captures intent + decisions made during a multi-round /spec session. It will be **regenerated from real code** (re-run /init) after the first scaffolding lands.

## Project overview

Interactive tool for **flavor / aroma formulation** work — most concretely, plant-based-meat product development. The user picks one or more **base** ingredients (e.g. pea protein) and one or more **target** ingredients (e.g. beef); the app renders the **union of all associated scents** as a multi-layer sunburst chart organized by a curated category taxonomy.

Future scope: textures (schema is ready; UI is not).

Hosted on the user's personal **Netlify** site as a fully static app.

Reference visuals that informed the design:
- Pangea Shellfish oyster flavor wheel — 3-ring sunburst.
- CoffeeMind Aroma Wheel — 2-ring sunburst.
- notbadcoffee.com flavor wheel — for the per-attribute "flavor card" pattern (definition + sensory anchors + parent navigation).

## Vocabulary (synonyms, used interchangeably)

- **scent** = **flavor** = **attribute** = **descriptor**
- **compound** = **chemical** = **molecule**
- **literature** = **paper(s)**
- **base** — source ingredient the user is starting from (per-wheel role).
- **target** — product/ingredient the user is trying to taste like (per-wheel role).
- **on-flavor / off-flavor** — **INTERNAL framing only.** Do NOT surface these labels in the UI. Many scents (`fresh`, `earthy`, `metallic`) are legitimately shared between bases and targets, and the on/off nomenclature is misleading. Provenance is metadata, not polarity.

## Stack

| Area | Decision |
|---|---|
| Architecture | **Static frontend + build-time Python curation.** Python runs only at build time to produce `bundle.json`. The deployed app is pure HTML/CSS/JS — no server, no cold starts, no iframe. |
| Frontend framework | **Svelte 5** (with Vite). Compiles to a small static bundle. |
| Visualization | **Plotly.js** `sunburst` chart, called from Svelte. (NOT Plotly Dash — this is the JS library, runs entirely in the browser.) |
| Curation language | **Python**, managed by **`uv`** (Astral). NOT pip / poetry. Build/validation scripts only; never deployed. |
| Schema validation | **Pydantic v2** at build time. The frontend trusts the bundle; no JSON Schema validator shipped to the browser. |
| In-browser PDF | **jsPDF + html2canvas** for client-side multi-page PDF (wheel page + optional definitions appendix). |
| State management | A single Svelte `writable()` store whose shape matches the **Wheel state** schema below; auto-synced to `localStorage`. Idiomatic Svelte. |
| Hosting target | **Netlify** (static). |
| Version control | **Git from day 1.** |

### Commands

This is a **two-language project** with a clear seam:

**Python side** (build-time only, never deployed):

```bash
uv sync                                    # install Python deps
uv add pydantic                            # add a Python dep
uv run python scripts/build_bundle.py      # regenerate frontend/static/bundle.json from data/source/*.json
uv run python scripts/fetch_compound.py 14302   # maintainer PubChem helper (deferred tooling)
uv run pytest                              # run Python tests
```

**Frontend side** (the deployed app):

```bash
cd frontend
npm install
npm run dev          # Vite dev server with hot reload
npm run build        # production build to frontend/dist/
npm run preview      # preview the production build
npm run test         # Vitest unit tests
npm run e2e          # Playwright end-to-end tests against the dev server
```

**Netlify build command** (configured in `netlify.toml`):

```
uv sync && uv run python scripts/build_bundle.py && cd frontend && npm install && npm run build
```

Publish directory: `frontend/dist/`.

## Data model

Curated JSON in `data/source/` is the source of truth, hand-edited by the maintainer. The Python build derives `frontend/static/bundle.json` from it. **Never edit `bundle.json` directly.**

### Conventions

- All IDs are **kebab-case slugs** (`cut-grass`, `pea-protein`, `2-acetyl-1-pyrroline`). Stable; renames are explicit migrations.
- Every record carries `deprecated: bool` (default `false`) for **soft-delete**. Files never shrink; past wheel exports keep resolving; the app warns on import when a referenced entity is deprecated.
- Every JSON file (curated AND exported wheel state) starts with `schema_version: 1`. The app rejects mismatches loudly. Wheel-state exports also carry `app_version`.

### Records

**Scent** — central record:
- `id` — slug (e.g. `"beany"`, `"cut-grass"`).
- `name` — canonical display name.
- `synonyms: list[str]` — alternative names that resolve to this scent (`["bean-like", "pea-like"]`).
- `domain: "scent" | "texture"` — texture is schema-ready; not in v1 UI.
- `definition` — short text, **user-authored**.
- `category_ids: list[str]` — a scent may belong to multiple categories (e.g., "earthy" in both "Vegetal" and "Mineral"). The wheel renders it under each.
- `compounds: list[str]` — compound `id` slugs (NOT raw CIDs).
- `sensory_anchors: list[{name, modality: "aroma" | "flavor", preparation_notes?}]` — real-world reference standards (inspired by the WCR Sensory Lexicon / notbadcoffee.com pattern). No numeric intensity.
- `literature: list[str]` — citation IDs.
- `default_color` — optional hex; overrides the category default.
- `deprecated: bool`.

**Ingredient**:
- `id`, `name`.
- `scents: list[str]` — flat list of scent IDs (no intensity).
- `deprecated: bool`.
- **No `kind: base | target` field** — role is per-wheel, chosen by the user when picking the ingredient for a wheel session. Same ingredient can be a base in one wheel and a target in another.

**Compound (molecule)**:
- `id` — slug. Universal canonical key inside this app.
- `cid` — PubChem CID (integer). Strongly preferred but **optional** (some niche compounds lack one).
- `name` — preferred display name (maintainer's choice).
- `synonyms: list[str]` — alternative names. Lookups by any synonym resolve to this `id`.
- `cas_number`, `smiles`, `formula`, `flavordb_url` — optional.
- `deprecated: bool`.
- `pubchem_url` is **derived**, not stored: `https://pubchem.ncbi.nlm.nih.gov/compound/<cid>`.

**Citation (paper / literature)**:
- `id` — slug.
- `title`, `authors: list[str]`, `year`.
- `doi`, `url` — at least one must be present.
- `journal`, `volume`, `pages`, `publisher` — optional.
- `source_kind: "journal" | "book_chapter" | "review" | "report"`.
- `local_pdf_filename` — optional filename in `Literature/` (path is implied — `Literature/<filename>`).
- `deprecated: bool`.

**Category (taxonomy node)** — flat list of nodes in `data/source/taxonomy.json`:
- `id`, `name`.
- `parent_id` — nullable; null means top-level. Parent-pointer tree (easier to validate than nested-children, easier to walk upward for breadcrumbs).
- `default_color` — optional hex.
- `deprecated: bool`.

### Reverse indexes (built once at app startup, used everywhere)

`load.py` (Python) and `data.js` (frontend) build these in-memory:

- `scent_id → list[ingredient_id]` — provenance: which ingredients have this scent.
- `compound_id → list[scent_id]` — which scents contribute this compound.
- `category_id → list[scent_id]` — which scents are in this category.
- `category_id → list[child_category_id]` — taxonomy children, for walking down.

**No junction files on disk.** Forward lists in JSON; reverse indexes are runtime artifacts.

### Wheel state (export / import / `localStorage` shape)

```jsonc
{
  "schema_version": 1,
  "app_version": "0.1.0",
  "name": "Pea-protein → beef formulation #3",
  "description": "...",
  "author": "Rebecca",
  "created_at": "...",
  "updated_at": "...",
  "ingredients": [
    {"ingredient_id": "pea-protein", "role": "base"},
    {"ingredient_id": "beef", "role": "target"}
  ],
  "scents_displayed": ["beany", "meaty", "earthy", ...],
  "custom_scents": [
    {"name": "user-coined name", "category_ids": ["..."], "definition": "..."}
  ],
  "color_overrides": {"beany": "#a4c639"},
  "hierarchy_depth": 3,
  "definitions_visible": false,
  "annotations": {"beany": "tried adding hexanal here, didn't work"}
}
```

## UI workflow

1. App loads → fetches `bundle.json`. Persistent **left sidebar** shows the ingredient picker (with role toggle: base or target) and the current scent list.
2. User selects 1+ **base** ingredients and 1+ **target** ingredients.
3. Wheel renders the **union of all associated scents** (deduplicated), organized by the **curated category taxonomy** (NOT by provenance). Default depth: 3 levels.
4. **Sidebar** lets the user:
   - Add or remove individual scents.
   - Add a **free-text custom scent**, scoped to this wheel only (does NOT enter the global library).
   - Configure hierarchy depth (collapsing deeper scents into their parent's slice — every selected scent is always represented at *some* level).
   - Toggle definitions on / off the wheel labels.
   - Edit per-scent colors (precedence: per-scent override > `Scent.default_color` > category default).
5. **Click a wedge** → **right side panel** opens, scrollable, showing in this order:
   - **Breadcrumb** of parent categories (e.g. `Vegetal › Green › Cut grass`).
   - **Definition.**
   - **Provenance** ("present in pea protein, beef").
   - **Sensory anchors** — list of real-world references with modality and optional preparation notes.
   - **Compounds** — name + CAS#, click-to-expand for SMILES / formula / external link.
   - **Literature** — structured citations, clickable DOI / URL.
   - **User notes** — per-wheel free-text annotation field.
6. **Export**: download as **SVG, PNG, PDF, or JSON**.
   - Download dialog includes an **"Include definitions"** checkbox (per-export choice, not a global preference).
   - **PDF**: wheel + name/description/author header + ingredient legend on page 1; if "Include definitions" is checked, an appended page (or pages) lists each displayed scent's name + definition.
   - **SVG / PNG**: single image; if "Include definitions" is checked, a definitions legend block is rendered below the wheel.
   - **JSON**: full wheel state regardless of the toggle.
7. **Persistence**:
   - Wheel state auto-persists to **browser `localStorage`** via a Svelte `writable()` store with a `subscribe()` → `localStorage.setItem()` side-effect. Hard cap at ~1 MB per wheel; if exceeded, prompt the user to export and clear.
   - User can **export wheel state JSON** and **import** it later to recreate a wheel exactly.

### Wheel layout rules
- Wedge layout is driven by the **curated taxonomy**, NOT by base/target provenance.
- Wedge weighting (v1) is **equal-area per leaf**.
- Color: **default palette by category**, with **per-scent override** allowed.
- Hierarchy depth is **user-configurable**; default is 3 levels on first render.
- Multiple base / target ingredients combine via **union with deduplication**.

### Side panel notes
- Breadcrumb of parents only (no sibling-jumps in v1).
- Full-screen / presentation mode is out of scope for v1.

## Edge cases & error states the app must handle

- **0 ingredients selected** → empty-state placeholder ("Pick a base ingredient to start").
- **Imported JSON has wrong `schema_version`** → fail loudly with expected vs. actual version; refuse to load (no silent upgrade).
- **Imported JSON references a deprecated or unknown scent / compound / ingredient** → load what resolves; show a non-blocking warning listing missing references.
- **Imported file is not valid JSON** → "Couldn't parse this file as JSON" and abort.
- **`localStorage` is disabled or full** → degrade gracefully: app keeps working in-memory; banner explains auto-save is off.
- **A scent has no compounds yet** → side panel: "No compounds recorded for this scent." (Empty state, not an error.)
- **An ingredient has no scents yet** → ingredient appears in picker with a "(no scents)" hint; selecting it shows an empty wheel.
- **PubChem REST is down** during the maintainer-side fetcher script → retry once, then fail with a clear error and a manual-workaround note. **Never blocks the deployed app** (which doesn't call PubChem).
- **Plotly.js fails to render** (data malformed in some way that passed validation but breaks Plotly's expectations) → catch the error, show "Couldn't render the wheel" with a diagnostic dump for bug reports.

## Security model

- **All user-supplied content renders as plain text only** — definitions, annotations, custom scent names, sensory anchor names, citation titles. No Markdown. No `{@html}`. No innerHTML. This eliminates the XSS surface from imported JSON files.
- **Imported JSON is validated structurally before any state mutation** — frontend uses a hand-rolled type guard or a small validator (e.g. Valibot or Zod). Invalid JSON never reaches the store.
- **No remote calls from the deployed app.** Everything runs in the browser; the only network activity is loading `bundle.json` from the same origin.

## v1 scope boundaries

- **Desktop-first.** Layout assumes ≥1024 px viewport. Mobile is out of scope; the 3-pane layout will not collapse meaningfully.
- **Data scale**: targeted ceiling for v1 is **~100 scents, ~500 compounds, ~50 citations, ~10 ingredients**. Exceeding these requires performance work that's not in v1 scope.
- **Single-user, single-language (English).** No auth, no multi-tenant, no i18n. If i18n ever happens, name/definition fields would migrate to `{lang: text}` maps.
- **No comparison mode** — one wheel at a time.
- **No textures yet** — schema supports them (`domain` flag); UI does not.
- **No intensity** modeled on any record. Equal-area is permanent for v1.
- **Accessibility**: WCAG 2.1 AA where reasonable. The sunburst chart itself is an inherent a11y weak point — defer a parallel data-table fallback to a future version.

## Reference data sources (used by the *maintainer*, not at runtime)

**Primary research corpus for target ingredients (animal proteins):**
- **`Literature/` folder** at the project root. 13 papers covering beef, chicken, pork, fish, lamb, turkey flavor chemistry; volatile organic compounds in meats; meat flavor precursors; meat-analogue texture and sensory profiling.
- Files prefixed with `0` / `00` are foundational. `00 maughan2012` is the single best multi-meat source for v1 targets (chicken, lamb, pork, beef, turkey).
- The two `0 Meat Analogues / Texture profiling` papers directly support the planned texture-domain expansion.

**Primary research tool for synthesizing across the corpus:**
- **<https://consensus.app>** — AI-powered scientific search that surfaces consensus findings across papers. Use it for questions like "what are the defining flavor attributes of beef?" rather than listing every attribute every paper mentions. This is the tool for deriving the curated taxonomy and per-target scent lists.

**Secondary cross-references (compounds + organoleptic prose):**
- **FlavorDB2** (IIIT Delhi) — ingredients → constituent molecules, with SMILES.
  Example: <https://cosylab.iiitd.edu.in/flavordb2/entity_details?id=271> (Beef).
- **The Good Scents Company (TGSC)** — per-molecule organoleptic prose.
  Example: <https://www.thegoodscentscompany.com/flavor/meaty.html>.
- **PubChem** — canonical CIDs, SMILES, formulas. See "Tooling" below for the validated REST endpoint.

**Definitions are user-authored.** TGSC and other DBs are research inputs to *you*; they are NOT auto-pulled into the app. The maintainer edits definitions directly in `data/source/scents.json`.

**Important — base-ingredient research is a separate effort.** The `Literature/` folder is target-side heavy. The base side (pea protein, soy protein, mycelium, wheat gluten off-flavors) needs its own research pass — additional papers, or a dedicated consensus.app session.

**Do NOT scrape any of these at runtime.** The deployed app reads only from `bundle.json`.

## Expected file layout

```
Sensory Wheel/
├── CLAUDE.md                       # this file
├── README.md                       # (TODO)
├── netlify.toml                    # Netlify build config (TODO)
├── .gitignore                      # (TODO)
│
├── pyproject.toml                  # uv-managed Python deps (TODO)
├── uv.lock                         # (TODO)
├── sensory_wheel/                  # Python package — build-time only (TODO)
│   ├── __init__.py
│   ├── schemas.py                  # Pydantic v2 models for every record type
│   ├── load.py                     # read data/source/, validate, build indexes
│   └── bundle.py                   # serialize to bundle.json shape
├── scripts/                        # Python entrypoints (TODO)
│   ├── build_bundle.py             # produce frontend/static/bundle.json
│   └── fetch_compound.py           # CID → PubChem REST → Compound record
│
├── data/source/                    # curated JSON, maintainer-edited (TODO)
│   ├── taxonomy.json               # category tree (parent_id pointers)
│   ├── scents.json
│   ├── compounds.json              # compound_id-keyed; cid optional
│   ├── citations.json              # from Literature/ + consensus.app
│   └── ingredients.json            # 5–10 plant-based-meat bases + targets
│
├── frontend/                       # Svelte 5 app — the deployed thing (TODO)
│   ├── package.json
│   ├── vite.config.js
│   ├── svelte.config.js
│   ├── index.html
│   ├── src/
│   │   ├── App.svelte              # 3-pane layout
│   │   ├── lib/
│   │   │   ├── store.js            # writable() for wheel state + localStorage sync
│   │   │   ├── data.js             # fetch bundle.json, expose lookups
│   │   │   ├── wheel.js            # build the Plotly.js sunburst figure
│   │   │   ├── pdf.js              # jsPDF + html2canvas export
│   │   │   └── exports.js          # SVG / PNG / JSON download
│   │   └── components/
│   │       ├── Sidebar.svelte
│   │       ├── Wheel.svelte        # Plotly.js wrapper
│   │       ├── SidePanel.svelte
│   │       └── Controls.svelte
│   ├── static/
│   │   └── bundle.json             # generated by Python build (gitignored)
│   ├── tests/
│   │   ├── unit/                   # Vitest
│   │   └── e2e/                    # Playwright
│   └── dist/                       # production build output (gitignored)
│
├── tests/                          # Python tests (TODO)
│   └── test_schemas.py             # Pydantic + load + index correctness
│
└── Literature/                     # ALREADY EXISTS — maintainer's PDFs
    └── (13 PDFs on meat/fish/poultry flavor + meat-analogue texture)
```

Two key conventions:
- **`data/source/*.json` is hand-edited.** This is truth. `frontend/static/bundle.json` is **derived** — never edit it directly.
- **`Literature/` is research material**, not app data. The app does not read from it. Citations derived from those papers go into `data/source/citations.json` (structured); a Citation's `local_pdf_filename` references a file in `Literature/`.

## Open items deferred to implementation

These are smaller decisions where deferring is cheap:

- Specific category-color palette (default hex per top-level category).
- Side panel transition (slide / dock / overlay) and width.
- PDF page size and exact layout details.
- Lint / format choice for Python (ruff likely; not committed).
- Lint / format choice for the frontend (prettier + eslint likely).
- Search / filter UX for the ingredient picker.
- Behavior when wheel becomes too dense (>50 scents).
- **Maintainer tooling**: the CID-driven PubChem fetcher script that auto-populates a Compound record (`name`, `synonyms`, `cas_number`, `smiles`, `formula`) from a single PubChem CID. Speeds curation; not user-facing.

## Tooling future sessions should reach for

**Build / scaffold:**
- `git init` and `.gitignore` (Python cache, `frontend/node_modules/`, `frontend/dist/`, `frontend/static/bundle.json`) **first**.
- `uv init` for the Python side; then `uv add pydantic`.
- `npm create vite@latest frontend -- --template svelte`; in `frontend/`, `npm install plotly.js-dist-min jspdf html2canvas`.
- `feature-dev` skill for guided build (code-explorer → code-architect → code-reviewer subagents).
- `frontend-design` skill for the sunburst + sidebar/side-panel polish.
- `design` skill if exploring visual variants of the wheel before committing to a layout.
- `superpowers:test-driven-development` and `superpowers:verification-before-completion` for discipline.

**UI debugging in the browser:**
- `mcp__Claude_Preview__*` — `preview_start` boots the Vite dev server, `preview_screenshot` captures the rendered wheel, `preview_click` / `preview_eval` exercise interactions and check console errors.
- `mcp__plugin_playwright_playwright__*` — Playwright for end-to-end tests of the pick-base → wheel-renders → click-wedge → panel-opens → export flow.
- `engineering:debug` and `superpowers:systematic-debugging` for reactivity / store-sync issues.

**Data layer:**
- **PubChem REST API** for the CID-driven compound fetcher. Validated endpoint:
  ```
  https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{CID}/property/Title,IUPACName,MolecularFormula,ConnectivitySMILES,InChIKey/JSON
  ```
  Note: PubChem renamed the SMILES field — use **`ConnectivitySMILES`** (not `CanonicalSMILES`).
  Synonyms endpoint: `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{CID}/synonyms/JSON`.
- WebFetch / WebSearch for FlavorDB2 entity pages and lexicon hunting.
- **Academic article MCP** (`mcp__e15fe6e9-*`): `search_articles` / `lookup_article_by_citation` / `get_article_metadata` to populate the literature layer and convert user-provided citations into the structured Citation schema.

**Project management:**
- `claude-md-management:revise-claude-md` to keep CLAUDE.md current as the project evolves.
- TodoWrite within sessions; Notion tools if research notes live there.

## Pointer for future sessions

**Regenerate this CLAUDE.md** (re-run /init) after the first scaffolding lands. At that point the **Commands** and **Architecture** sections should reflect real code, not intent. The "Status" section above should disappear.
