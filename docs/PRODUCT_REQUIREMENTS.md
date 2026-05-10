# Sensory Wheel — Product Requirements

**Owner**: Rebecca Miller
**Version**: 0.1.0 | **Last updated**: 2026-05-10
**Success metric**: % of 5×5 ingredients populated end-to-end (scents + compounds + citations) + capabilities done
**Current coverage**: 0/5 bases populated, 0/5 targets populated, 0/17 capabilities done — starting state; updates as work lands

---

## Problem

Plant-based-meat formulation is a masking and mimicry problem: plant proteins (pea, soy, mycelium, wheat gluten, faba bean) carry inherent off-notes — beany, grassy, chalky, oxidized — that must be suppressed, while the defining flavor signatures of animal proteins (beef, chicken, pork, fish, lamb) must be built up through flavor chemistry and ingredient choices. There is no interactive tool that lets a formulator see the full aroma landscape of a chosen base and target side-by-side, drill into individual scents to see their constituent compounds and literature citations, and export the analysis for documentation. Formulators rely on paper references and mental models, which slows research and makes it hard to share insights across sessions.

(Note: while internal terminology distinguishes off-flavors from bases and on-flavors from targets, the user-facing UI never uses these labels — many scents like "fresh" or "earthy" belong on both sides depending on context.)

## Vision

The Sensory Wheel gives a food scientist or formulator a single interactive surface: pick a base ingredient and a target, see the union of all associated scents rendered as a multi-layer sunburst organized by a curated aroma taxonomy, click any wedge to open a scrollable side panel with definition, sensory anchors, compounds, and citations, and export the finished wheel as SVG, PNG, PDF, or JSON. Wheel state auto-saves to the browser and can be re-imported. The result is a deployable static app — no server, no login — that demonstrates the full flavor-chemistry research workflow for a 5-base × 5-target ingredient matrix.

---

## MoSCoW Status

The heartbeat of this document. Scan this table to know where everything stands.

| # | Code | Capability | Priority | Status | Section |
|---|------|------------|----------|--------|---------|
| 1 | WV | Wheel Visualization | Must | Not started | [#1](#1-wheel-visualization-wv) |
| 2 | IP | Ingredient Picker | Must | Not started | [#2](#2-ingredient-picker-ip) |
| 3 | SM | Scent Management Sidebar | Must | Not started | [#3](#3-scent-management-sidebar-sm) |
| 4 | SP | Side Panel Detail View | Must | Not started | [#4](#4-side-panel-detail-view-sp) |
| 5 | HD | Hierarchy Depth Control | Must | Not started | [#5](#5-hierarchy-depth-control-hd) |
| 6 | LS | localStorage Persistence | Must | Not started | [#6](#6-localstorage-persistence-ls) |
| 7 | IO | JSON Import/Export | Must | Not started | [#7](#7-json-importexport-io) |
| 8 | CD | Curation Data Pipeline | Must | Not started | [#8](#8-curation-data-pipeline-cd) |
| 9 | CN | Curated Content (5×5) | Must | Not started | [#9](#9-curated-content-55-cn) |
| 10 | CC | Color Customization | Should | Not started | [#10](#10-color-customization-cc) |
| 11 | CS | Custom Free-text Scents | Should | Not started | [#11](#11-custom-free-text-scents-cs) |
| 12 | DT | Definitions Toggle | Should | Not started | [#12](#12-definitions-toggle-dt) |
| 13 | DL | Multi-format Download (SVG/PNG/PDF) | Should | Not started | [#13](#13-multi-format-download-svgpngpdf-dl) |
| 14 | AN | Per-wheel Annotations | Should | Not started | [#14](#14-per-wheel-annotations-an) |
| 15 | AC | Accessibility Fallback | Could | Not started | [#15](#15-accessibility-fallback-ac) |
| 16 | RM | README Polish | Could | Not started | [#16](#16-readme-polish-rm) |
| 17 | — | Won't (v1): Texture UI · Comparison Mode · Mobile · i18n · Auth | Won't | — | [#17](#17-wont-have-v1) |

<details>
<summary><strong>Status Definitions &amp; Maintenance Rules</strong> (click to expand)</summary>

Feature status is **derived from codebase evidence**, not authored from memory. The codebase is the source of truth.

**Feature-level status** (base facts — in each capability's feature table):

| Status | Evidence required |
|--------|------------------|
| `Not started` | No implementation files exist for this feature |
| `In progress` | Implementation exists but: tests missing or failing, incomplete, or not yet deployed |
| `Bug (description)` | Implementation exists but has a known runtime or visual failure |
| `Done` | Implementation exists + tests pass + deployed to production + working end-to-end |

**Capability-level status** (derived — rolled up in MoSCoW table):

| Status | Rule |
|--------|------|
| `Not started` | Every feature row is `Not started` |
| `In progress (detail)` | At least one feature started; any Must-have feature is incomplete |
| `Partial (detail)` | All Must-have features are `Done`; Should-have features remain |
| `Done` | All Must-have + Should-have features are `Done` |

**Header metrics**: `X/5 bases populated` = ingredients in `data/source/ingredients.json` with at least 1 scent, 1 compound, and 1 citation recorded. Same definition for `X/5 targets populated`. `X/17 capabilities done` = capabilities whose MoSCoW row reads `Done`.

**Refresh scope**: When updating any feature in capability #N, re-derive the entire capability — all its feature rows, the MoSCoW summary row, Known Issues, and header metrics if affected. If a commit touches code that serves multiple capabilities, re-derive all affected capabilities.

</details>

---

## What's Already Built

> Derived from feature tables below. The capability section's feature row is authoritative.

| Feature | Capability |
|---------|-----------|
| Documentation suite (`docs/` folder) — [BUSINESS_RULES.md](./BUSINESS_RULES.md), [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md), [WORKFLOWS.md](./WORKFLOWS.md), and this PRD | Pre-implementation infrastructure |

---

## 1. Wheel Visualization (WV)

`Must-have` | Not started

**Goal**: Render a multi-layer sunburst chart from `bundle.json` that shows the union of all selected ingredient scents, organized by the curated aroma taxonomy. The wheel is the primary visual output of the app.

**User story**: As a formulator, I want to see the full aroma landscape of my chosen base and target rendered as an interactive sunburst so that I can quickly identify shared and unique scent attributes without consulting multiple papers.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Render sunburst from `bundle.json` | Must | Not started | `Wheel.svelte` wraps Plotly.js `sunburst` trace; data built by `wheel.js` from the Svelte store |
| Hover tooltip on wedge | Must | Not started | Show scent name + category breadcrumb; Plotly default hover |
| Click wedge to open side panel | Must | Not started | `Wheel.svelte` emits event on Plotly `plotly_click`; `App.svelte` routes to `SidePanel.svelte` |
| Equal-area weighting per leaf | Must | Not started | v1 wedge sizing is equal-area — no intensity modeling |
| Empty-state placeholder | Must | Not started | When 0 ingredients selected: "Pick a base ingredient to start" message in wheel area |
| Error state on Plotly render failure | Should | Not started | Catch Plotly errors; show "Couldn't render the wheel" with diagnostic dump |
| Demo pre-load on first visit | Should | Not started | First-load shows pre-populated demo: soy (base) + beef (target) |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #8 (CD — bundle.json must exist with valid data); Capability #9 (CN — curated scent data); Capability #2 (IP — ingredient selection drives the wheel).

<details>
<summary>Chart specifications</summary>

### Sunburst Chart

Rendering conventions (library build, script loading, color model, container) are defined in [Plotly.js Chart Conventions](#plotlyjs-chart-conventions) and not restated here.

- **Data source**: `bundle.json` fetched from same origin at app startup; wheel data computed by `wheel.js`
- **Hierarchy**: Category taxonomy drives the ring structure. Top-level categories (Floral, Fruity, Vegetal, Roasted, Spicy, Animal, Mineral, Off-notes) are the first ring; subcategories form inner rings; scents are the leaf wedges.
- **Scent union**: `wheel.js` computes the deduplicated union of all `scents[]` arrays from selected ingredients. A scent appearing in multiple ingredients appears once.
- **Weighting**: Equal-area per leaf (v1). All leaf wedges share the same angular size within their parent slice.
- **Depth**: User-configurable (see [#5 HD](#5-hierarchy-depth-control-hd)). Default: 3 levels on first render.
- **Multi-category scents**: A scent with `category_ids: ["vegetal", "mineral"]` appears in both parent slices. `wheel.js` duplicates the leaf entry for each category.
- **Click behavior**: Plotly `plotly_click` event on any wedge → `App.svelte` opens `SidePanel.svelte` for that scent.
- **Hover tooltip**: Shows scent name + category breadcrumb via Plotly default hover.

### Interaction Flow

1. User picks ingredient(s) → store updates → `wheel.js` recomputes → Plotly re-renders.
2. User hovers wedge → Plotly tooltip shows scent name and category path.
3. User clicks wedge → Plotly `plotly_click` event → `App.svelte` opens `SidePanel.svelte` for that scent.
4. User scrolls/pinches → Plotly zoom (native). No custom zoom handling needed.

</details>

---

## 2. Ingredient Picker (IP)

`Must-have` | Not started

**Goal**: A persistent left sidebar panel where the user selects one or more base ingredients and one or more target ingredients. The picker drives the wheel and all downstream state.

**User story**: As a formulator, I want to pick pea protein as my base and beef as my target so that the wheel immediately updates to show the combined aroma landscape I am trying to navigate.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| List all non-deprecated ingredients | Must | Not started | `data.js` filters `deprecated === true` before populating picker; see [BUSINESS_RULES.md §2](./BUSINESS_RULES.md#2-ingredient) |
| Role toggle per ingredient (base / target) | Must | Not started | Each selected ingredient has a role assignment; role stored in Wheel State `ingredients[]` |
| Add / remove ingredient from wheel | Must | Not started | Selection mutates the Svelte store; wheel re-renders reactively |
| "(no scents)" hint on empty ingredient | Must | Not started | Ingredient with empty `scents[]` shows a hint; selecting it produces an empty wheel |
| Search / filter within picker | Should | Not started | Text filter to narrow the ingredient list; UX TBD at implementation |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #8 (CD — bundle.json must contain `ingredients` data); Capability #6 (LS — selections persist to localStorage).

---

## 3. Scent Management Sidebar (SM)

`Must-have` | Not started

**Goal**: The left sidebar (below or alongside the ingredient picker) lets the user view, add, and remove individual scents from the current wheel, and access wheel-level controls. This is the primary manipulation surface for the wheel's content.

**User story**: As a formulator, I want to remove a specific scent from the wheel and add a custom one I've observed in the lab so that my wheel reflects my actual sensory experience rather than only the curated data.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Display list of current wheel scents | Must | Not started | Derived from selected ingredients' `scents[]` union; updates reactively |
| Remove individual scent from display | Must | Not started | Removes from `scents_displayed[]` in Wheel State; wheel re-renders |
| Add scent from global library | Must | Not started | Search / browse `bundle.json` scents not already on the wheel; add to `scents_displayed[]` |
| Add custom free-text scent | Should | Not started | See [#11 CS](#11-custom-free-text-scents-cs) — tracked separately |
| Hierarchy depth control | Must | Not started | See [#5 HD](#5-hierarchy-depth-control-hd) — tracked separately |
| Definitions toggle | Should | Not started | See [#12 DT](#12-definitions-toggle-dt) — tracked separately |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #1 (WV — sidebar mutations re-render the wheel); Capability #6 (LS — sidebar state persists).

---

## 4. Side Panel Detail View (SP)

`Must-have` | Not started

**Goal**: When the user clicks a wedge, a right-side scrollable panel opens showing the full detail record for that scent: breadcrumb, definition, provenance, sensory anchors, compounds, literature, and the per-wheel annotation field.

**User story**: As a food scientist, I want to click the "beany" wedge and immediately see which compounds cause it, what the literature says, and what real-world reference standards I can use to train my panel so that I can make informed formulation decisions.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Breadcrumb of parent categories | Must | Not started | E.g. `Vegetal › Green › Cut grass`; parents only, no sibling navigation in v1 |
| Definition display | Must | Not started | Plain-text rendering; see [BUSINESS_RULES.md §7](./BUSINESS_RULES.md#7-cross-cutting) XSS guard |
| Provenance ("present in…") | Must | Not started | Built from reverse index `scent_id → list[ingredient_id]`; see [SYSTEM_ARCHITECTURE.md §4.2](./SYSTEM_ARCHITECTURE.md#42-entity-relationship-diagram) |
| Sensory anchors list | Must | Not started | `name` + `modality` + optional `preparation_notes`; plain-text only |
| Compounds list | Must | Not started | `name` + CAS#; click-to-expand for SMILES / formula / PubChem link |
| "No compounds recorded" empty state | Must | Not started | Shown when `compounds[]` is empty; not an error |
| Literature citations | Must | Not started | Structured: title + authors + year + DOI/URL link |
| Per-wheel annotation field | Must | Not started | Free-text; stored in `annotations` map in Wheel State; plain-text rendering |
| PubChem link (when cid present) | Should | Not started | Derived URL: `https://pubchem.ncbi.nlm.nih.gov/compound/<cid>`; only shown when `cid != null` |
| Deprecated compound / citation filtering | Should | Not started | `SidePanel.svelte` filters on `deprecated` before rendering lists |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #1 (WV — click event triggers panel open); Capability #8 (CD — bundle must contain compound and citation data); Capability #14 (AN — annotation field).

<details>
<summary>Interaction specifications</summary>

### Panel Layout (top to bottom)

1. **Breadcrumb** — `Category › Subcategory › Scent name`. Clicking a category label is not wired in v1 (no sibling navigation).
2. **Definition** — Short paragraph. Plain text. If `definition` is null, show "No definition recorded."
3. **Provenance** — "Present in: [pea protein, beef]." Built from the reverse `scent_id → ingredient_id[]` index in `data.js`.
4. **Sensory anchors** — Bulleted list: each anchor's `name` (modality label in muted text), optional `preparation_notes` on second line. Aroma vs. flavor modality distinguished visually.
5. **Compounds** — Collapsed card list. Each card shows `name` + `cas_number`. Click to expand: SMILES, molecular formula, PubChem link (if `cid` is set). Deprecated compounds are excluded.
6. **Literature** — Citation list. Each entry: `title` (plain text), `authors` truncated, `year`, DOI or URL as clickable link. Deprecated citations are excluded.
7. **Annotation** — Textarea bound to `annotations[scent_id]` in Wheel State. Placeholder: "Add a note about this scent…". Auto-saves to localStorage on blur.

### Open / Close Behavior

- Click wedge → panel slides in from right (transition TBD at implementation; slide or dock).
- Click the same wedge again or press Escape → panel closes.
- Switching between wedges: panel stays open, content swaps.
- Panel width: TBD at frontend-design phase. Minimum: 320 px.
- Full-screen / presentation mode: out of scope for v1.

</details>

---

## 5. Hierarchy Depth Control (HD)

`Must-have` | Not started

**Goal**: Let the user collapse or expand the number of visible rings in the sunburst so that dense wheels remain readable. Every selected scent is always represented at some level — no scent is silently hidden.

**User story**: As a formulator, I want to collapse the wheel to 2 levels when there are too many scents so that I can still see the category-level picture without the chart becoming an unreadable ring.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Depth slider or +/− control in sidebar | Must | Not started | Adjusts `hierarchy_depth` in Wheel State; wheel re-renders |
| Default depth: 3 on first render | Must | Not started | `hierarchy_depth: 3` in default Wheel State |
| Depth ≥ 1 enforced | Must | Not started | See [BUSINESS_RULES.md §6](./BUSINESS_RULES.md#6-wheel-state) — `hierarchy_depth` is a positive integer |
| Scents always represented at some level | Must | Not started | When depth is reduced, scents collapse into their nearest visible ancestor's slice |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #1 (WV — depth change re-renders the wheel); Capability #3 (SM — control lives in the sidebar).

---

## 6. localStorage Persistence (LS)

`Must-have` | Not started

**Goal**: Wheel state auto-saves to the browser `localStorage` on every change so that the user never loses work on refresh. The app degrades gracefully if `localStorage` is unavailable.

**User story**: As a formulator, I want my ingredient selections and annotations to still be there when I refresh the page so that I don't have to re-build my wheel from scratch every session.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Auto-save on every store mutation | Must | Not started | `store.js` `subscribe()` → `localStorage.setItem('sensory_wheel_state', ...)` |
| Load from localStorage on app startup | Must | Not started | `store.js` reads and validates on init; `schema_version` check per [BUSINESS_RULES.md §6](./BUSINESS_RULES.md#6-wheel-state) |
| ~1 MB per-wheel size cap | Must | Not started | `store.js` checks `JSON.stringify(state).length` before each `setItem()`; prompt to export if exceeded |
| Graceful degradation when localStorage unavailable | Must | Not started | `try/catch` around `setItem()`; persistent banner "Auto-save is off"; app continues in-memory |
| Schema version mismatch → discard stored state | Must | Not started | On mismatch, clear stored state; prompt user to start fresh or import a compatible export |

**Known issues**: None — pre-implementation.

**Dependencies**: None. `store.js` is a standalone module.

---

## 7. JSON Import/Export (IO)

`Must-have` | Not started

**Goal**: The user can export the current wheel state as a JSON file and re-import it later to recreate the wheel exactly. Imported JSON is validated structurally before any state mutation.

**User story**: As a formulator, I want to export my pea-protein → beef wheel as JSON, share it with a colleague, and have them import it to see exactly the same wheel so that we can collaborate on formulation notes asynchronously.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Export current wheel state as JSON | Must | Not started | Downloads `wheel_state.json` with `schema_version: 1` + `app_version`; full state regardless of definitions toggle |
| Import JSON via file picker | Must | Not started | `JSON.parse()` in `try/catch`; parse failure → user-facing error, state unchanged |
| Structural type guard before store update | Must | Not started | Hand-rolled or Zod/Valibot type guard; invalid shape → user-facing error |
| `schema_version` mismatch → hard reject | Must | Not started | Fail loudly: "expected schema_version 1, got X"; do not silently upgrade; see [BUSINESS_RULES.md §7](./BUSINESS_RULES.md#7-cross-cutting) |
| Deprecated / unknown refs → non-blocking warning | Must | Not started | Load what resolves; surface single warning listing all missing references |
| Deprecated Ingredient in import → warning | Must | Not started | Same warning pattern; state loaded with the deprecated reference noted |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #6 (LS — import calls `store.set()`); Capability #13 (DL — JSON download is one of the export formats).

---

## 8. Curation Data Pipeline (CD)

`Must-have` | Not started

**Goal**: A Python build pipeline that validates hand-edited `data/source/*.json` using Pydantic v2 and produces `frontend/static/bundle.json`. Invalid source data aborts the build; the previous deploy stays live.

**User story**: As the maintainer, I want my edits to `data/source/scents.json` to be validated automatically before they reach the deployed app so that I can't accidentally publish malformed data.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Pydantic v2 models for all entities | Must | Not started | `sensory_wheel/schemas.py` — Scent, Ingredient, Compound, Citation, Category, SensoryAnchor |
| `load.py` parses and validates all source files | Must | Not started | Reads `data/source/*.json`; runs cross-entity referential integrity checks |
| Cross-entity referential integrity checks | Must | Not started | Every `category_ids`, `compounds`, `literature`, `scents` foreign ID must resolve; see [BUSINESS_RULES.md](./BUSINESS_RULES.md) |
| `bundle.py` serializes validated data + reverse indexes | Must | Not started | Writes `frontend/static/bundle.json`; includes pre-built reverse index maps |
| `scripts/build_bundle.py` entrypoint | Must | Not started | Calls `load.py` + `bundle.py`; exits non-zero on any ValidationError |
| Build fails loudly on validation error | Must | Not started | Descriptive error: entity type + ID + field; see [WORKFLOWS.md §3](./WORKFLOWS.md#3-build-pipeline) |
| `scripts/fetch_compound.py` PubChem helper | Should | Not started | Maintainer-side tool only; CID → PubChem PUG REST → Compound record draft; see [WORKFLOWS.md §6](./WORKFLOWS.md#6-pubchem-fetcher-workflow) |
| Python tests for schemas + referential integrity | Should | Not started | `tests/test_schemas.py`; run with `uv run pytest` |

**Known issues**: None — pre-implementation.

**Dependencies**: None for the Python pipeline itself. Downstream: all frontend capabilities depend on `bundle.json` existing.

---

## 9. Curated Content (5×5) (CN)

`Must-have` | Not started — 0/5 bases populated, 0/5 targets populated

**Goal**: Hand-curate structured JSON for all 5 base × 5 target ingredients, covering scents, compounds, and citations for each. This is the content milestone that proves the tool with real flavor chemistry data.

**User story**: As a portfolio visitor or food scientist, I want to explore the pea protein → beef wheel with real compound data and literature citations so that I can assess the scientific depth of the tool and apply the insights to my own formulation work.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Taxonomy (`taxonomy.json`) — 8 top-level categories | Must | Not started | Floral, Fruity, Vegetal, Roasted, Spicy, Animal, Mineral, Off-notes; subcategories TBD per research |
| 5 base ingredients with scents | Must | Not started | Pea protein, soy, mycelium, wheat gluten, faba bean; scent lists derived from `Literature/` + consensus.app |
| 5 target ingredients with scents | Must | Not started | Beef, chicken, pork, fish, lamb; primary source: `Literature/00 maughan2012` and corpus |
| Compounds for all scents | Must | Not started | Per-scent `compounds[]` list; CIDs sourced via `fetch_compound.py`; see [WORKFLOWS.md §6](./WORKFLOWS.md#6-pubchem-fetcher-workflow) |
| Citations for all scents | Must | Not started | Structured Citation records from `Literature/` PDFs + consensus.app; at least 1 per scent |
| Scent definitions | Should | Not started | User-authored per scent; TGSC / FlavorDB2 are research inputs only — not auto-pulled |
| Sensory anchors per scent | Should | Not started | Real-world reference standards (name + modality + optional preparation_notes) |

**Known issues**: None — pre-implementation. Content curation is the primary throughput risk; see [SYSTEM_ARCHITECTURE.md §9.4](./SYSTEM_ARCHITECTURE.md#94-content-curation-throughput).

**Dependencies**: Capability #8 (CD — pipeline must exist before content can be validated); `Literature/` folder (already populated with 13 PDFs); consensus.app for synthesis.

---

## 10. Color Customization (CC)

`Should-have` | Not started

**Goal**: Let the user override the display color for any individual scent in the current wheel. Color overrides are stored in Wheel State and travel with JSON exports.

**User story**: As a formulator, I want to highlight the "beany" scent in red so that it stands out as my primary masking challenge when I share the wheel with my team.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Per-scent color picker in sidebar or side panel | Should | Not started | Produces a hex color override stored in `color_overrides` map in Wheel State |
| Color resolution precedence enforced | Should | Not started | Per-scent override > `Scent.default_color` > category `default_color`; see [BUSINESS_RULES.md §6](./BUSINESS_RULES.md#6-wheel-state) |
| Hex format validation on import | Should | Not started | `^#[0-9a-fA-F]{6}$`; invalid values discarded with a warning; see [BUSINESS_RULES.md §7](./BUSINESS_RULES.md#7-cross-cutting) |
| Reset to default color | Should | Not started | Removes the entry from `color_overrides` map |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #1 (WV — color change re-renders the wheel); Capability #6 (LS — overrides persist).

---

## 11. Custom Free-text Scents (CS)

`Should-have` | Not started

**Goal**: Let the user add a scent that doesn't exist in the global library — e.g., one observed in the lab that hasn't been catalogued. Custom scents are scoped to the current wheel only and never enter the curated data.

**User story**: As a formulator, I want to add a custom scent called "plasticky off-note" to my wheel so that I can document a novel observation without needing to edit the global library.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| "Add custom scent" field in sidebar | Should | Not started | Name input + category assignment (pick from taxonomy); stored in `custom_scents[]` in Wheel State |
| Custom scents scoped to current wheel only | Should | Not started | Never merged into bundle.json; `data.js` keeps custom scents in a separate collection |
| Plain-text rendering of custom scent name / definition | Should | Not started | XSS guard; see [BUSINESS_RULES.md §7](./BUSINESS_RULES.md#7-cross-cutting) |
| Custom scent appears in wheel and sidebar | Should | Not started | `wheel.js` includes custom scents in the Plotly trace |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #3 (SM — custom scent entry lives in the sidebar); Capability #1 (WV — custom scents appear in the wheel).

---

## 12. Definitions Toggle (DT)

`Should-have` | Not started

**Goal**: A toggle that shows or hides scent definitions directly on the wheel wedge labels (or as a tooltip layer). Provides additional context without requiring a side panel click.

**User story**: As a portfolio visitor, I want to toggle definitions on the wheel so that I can read what each scent means without clicking into every wedge individually.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Toggle control in sidebar | Should | Not started | Updates `definitions_visible: bool` in Wheel State |
| Wheel labels include definition text when toggled on | Should | Not started | Implementation TBD (Plotly label customization or tooltip layer) |
| Per-export override | Should | Not started | "Include definitions" checkbox at export time; independent of the global toggle; see [#13 DL](#13-multi-format-download-svgpngpdf-dl) |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #1 (WV — toggle affects rendering); Capability #13 (DL — per-export definitions option).

---

## 13. Multi-format Download (SVG/PNG/PDF) (DL)

`Should-have` | Not started

**Goal**: Users can download the wheel as SVG, PNG, PDF, or JSON. PDF includes a name/description header and an optional definitions appendix.

**User story**: As a food scientist, I want to export a PDF of my pea-protein → beef wheel with definitions included so that I can attach it to a project brief without any manual formatting.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Export dialog with format selector | Should | Not started | SVG, PNG, PDF, JSON tabs or radio; "Include definitions" checkbox |
| SVG download | Should | Not started | Single image export from Plotly; if definitions checked, definitions legend block appended below wheel image |
| PNG download | Should | Not started | Same as SVG but rasterized; if definitions checked, definitions legend block rendered below wheel image |
| PDF download (jsPDF + html2canvas) | Should | Not started | Page 1: wheel + name/description/author header + ingredient legend. Optional page 2+: definitions appendix per displayed scent |
| JSON download | Must | Not started | Full wheel state; always exported regardless of definitions toggle; see [#7 IO](#7-json-importexport-io) |
| "Include definitions" checkbox | Should | Not started | Per-export choice; does not affect `definitions_visible` in Wheel State |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #12 (DT — definitions toggle state informs default); Capability #7 (IO — JSON export is part of this flow).

<details>
<summary>Export specifications</summary>

### SVG / PNG

- **Source**: Plotly's built-in SVG export (`Plotly.downloadImage`).
- **Definitions legend** (when "Include definitions" checked): rendered as a separate HTML block below the wheel via html2canvas, then composited. Each entry: scent name (bold) + definition (plain text). Layout: two-column grid, alphabetical order.
- **Filename**: `sensory-wheel-<name>-<date>.svg` / `.png`

### PDF (jsPDF + html2canvas)

- **Page 1 layout**:
  - Header: wheel name (H1), description (paragraph), author, date generated.
  - Ingredient legend: two columns — "Base: [pea protein]" and "Target: [beef]".
  - Wheel image: html2canvas capture of the rendered Plotly chart at full quality.
- **Page 2+ (definitions appendix)** — only when "Include definitions" checked:
  - Title: "Scent Definitions"
  - Table: two columns — scent name, definition. Sorted by taxonomy order.
  - Plain text only; no Markdown or HTML rendering.
- **Page size**: A4 or Letter (TBD at frontend-design phase).
- **Filename**: `sensory-wheel-<name>-<date>.pdf`

### JSON

- Full `WheelState` object. `schema_version: 1`. `app_version` at time of export. No filtering by definitions toggle.
- See [BUSINESS_RULES.md §6](./BUSINESS_RULES.md#6-wheel-state) for the complete Wheel State shape.
- **Filename**: `sensory-wheel-<name>-<date>.json`

</details>

---

## 14. Per-wheel Annotations (AN)

`Should-have` | Not started

**Goal**: Each scent on the wheel can carry a free-text note scoped to the current wheel session. Notes are stored in `localStorage` and travel with JSON exports.

**User story**: As a formulator, I want to annotate the "beany" scent with "tried hexanal at 10 ppm — no effect" so that I can track what I've already attempted without leaving the app.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Annotation textarea in side panel | Should | Not started | Bound to `annotations[scent_id]` in Wheel State; auto-saves on blur |
| Annotations persist to localStorage | Should | Not started | Via Wheel State auto-save; see [#6 LS](#6-localstorage-persistence-ls) |
| Annotations travel with JSON export / import | Should | Not started | Part of Wheel State `annotations` map |
| Plain-text rendering | Should | Not started | XSS guard; see [BUSINESS_RULES.md §7](./BUSINESS_RULES.md#7-cross-cutting) |

**Known issues**: None — pre-implementation.

**Dependencies**: Capability #4 (SP — annotation field lives in the side panel); Capability #6 (LS — annotations persist).

---

## 15. Accessibility Fallback (AC)

`Could-have` | Not started

**Goal**: Provide a parallel data-table view of the wheel's content for users who cannot or choose not to use the sunburst chart. WCAG 2.1 AA compliance where reasonable; the sunburst itself is an inherent a11y weak point.

**User story**: As a screen-reader user, I want a data table listing all displayed scents, their categories, and their definitions so that I can access the wheel's content without relying on the visual chart.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| "Switch to table view" toggle | Could | Not started | Replaces wheel area with a flat sortable table; wheel controls still operate |
| Table columns: scent name, category, definition | Could | Not started | Subset of full detail; click row to open side panel |
| ARIA labels on interactive wheel elements | Could | Not started | Best-effort; Plotly's sunburst has limited native ARIA support |

**Known issues**: None — pre-implementation. This is explicitly a deferred concern per [CLAUDE.md](../CLAUDE.md) v1 scope boundaries.

**Dependencies**: Capability #1 (WV — table view is an alternate rendering of the same data).

---

## 16. README Polish (RM)

`Could-have` | Not started

**Goal**: The public-facing `README.md` — aimed at GitHub visitors who are food scientists or developers — has a hero screenshot or GIF of the wheel, a live demo link, a clear project description, and complete quick-start instructions.

**User story**: As a portfolio visitor, I want to see a screenshot of the wheel and a demo link in the README so that I can immediately understand what the project does without cloning it.

| Feature | Priority | Status | Notes |
|---------|----------|--------|-------|
| Hero screenshot or GIF of wheel in README | Could | Not started | Requires a deployed app to capture from |
| Live demo link (Netlify URL) | Could | Not started | Requires Netlify deploy |
| Quick-start instructions tested end-to-end | Could | Not started | `git clone` → `uv sync` → `npm install` → `npm run dev` path verified |
| Credits section | Could | Not started | FlavorDB2, TGSC, PubChem, Literature corpus authors, consensus.app |

**Known issues**: None — pre-implementation. README content depends on a working deployed instance, so this capability is intentionally last.

**Dependencies**: All Must-have capabilities done; a Netlify deployment active.

---

## 17. Won't-Have (v1)

These are explicitly out of scope for v1. The schema and architecture are designed to accommodate future expansion without rework.

| Capability | Reason |
|-----------|--------|
| **Texture Domain UI** | `domain: "texture"` flag is schema-ready; all records support it; but the UI, wheel rendering, and sidebar panel for texture descriptors are deferred. Adding texture UI is a well-defined future capability. |
| **Comparison Mode** | One wheel at a time. Comparing two wheels side-by-side (e.g., pea vs. soy against beef) is deferred to v2. The single-wheel model keeps the UI scope tractable. |
| **Mobile** | Desktop-first. The 3-pane layout (sidebar + wheel + side panel) does not collapse meaningfully below 1024 px. Mobile is out of scope; no responsive breakpoints are planned for v1. |
| **i18n** | English only. If internationalization is added later, `name` and `definition` fields would migrate to `{lang: text}` maps. |
| **Auth / Multi-tenant** | Single-user, no login. Hosted as a public static app. No user accounts, no per-user data server-side. |

---

## Plotly.js Chart Conventions

Charts use a single visual identity across the app — the sunburst wheel is the only chart type in v1. Conventions:

| Convention | Detail |
|-----------|--------|
| Library | Plotly.js, slim `plotly.js-strict-dist-min` build (~800 KB uncompressed, ~250 KB gzipped) |
| Chart type | `sunburst` |
| Interactivity | Plotly defaults: hover tooltips, click-to-select, scroll-to-zoom, pan |
| Container | `<div>` per `Wheel.svelte` component; fixed dimensions; desktop-optimized |
| Sizing | Desktop-optimized (≥1024 px viewport); not responsive in v1 |
| Script loading | Plotly.js imported once at the `Wheel.svelte` component level — NEVER re-imported per-render or in partial templates |
| Color | Per-category default palette; per-scent overrides applied at render time via `wheel.js` |
| Export | SVG and PNG via `Plotly.downloadImage`; PDF via jsPDF + html2canvas capture of the Plotly container |

---

## Architecture Constraints

These are load-bearing decisions. Do not change without understanding consequences. Full definitions live in [CLAUDE.md](../CLAUDE.md) "Load-Bearing Decisions" and "Constraints."

| Constraint | Why |
|-----------|-----|
| `data/source/*.json` is truth; `bundle.json` is derived | Editing `bundle.json` directly bypasses Pydantic validation and breaks the integrity guarantee. Never edit the bundle. |
| All IDs are kebab-case slugs | Slug regex `^[a-z0-9]+(-[a-z0-9]+)*$` enforced by Pydantic on all entities; see [BUSINESS_RULES.md §7](./BUSINESS_RULES.md#7-cross-cutting). Stable; renames require explicit migration. |
| `schema_version` exact match | Mismatch on wheel-state import → hard reject with clear error; no silent upgrade. Mismatch on curated files → build aborts. |
| Soft-delete; files never shrink | `deprecated: true` instead of deletion. Past wheel exports keep resolving deprecated references. Hard deletion is prohibited. |
| Plain-text rendering for user content | All user-supplied fields (definitions, annotations, custom scent names, citation titles) render as plain text only — no `{@html}`, no Markdown. XSS surface from imported JSON is eliminated. |
| Build-time bundle; no live scraping | The deployed app reads only from `bundle.json` at the same origin. No PubChem, FlavorDB2, or TGSC calls from the browser. |
| Plotly.js loaded once | Plotly is imported once in `Wheel.svelte`; not per render or per page. |

---

## Data Flow Reference

| Data type | Source of truth | Sync path | Latency |
|-----------|----------------|-----------|---------|
| Curated source data | Maintainer hand-edits `data/source/*.json` | Manual edit → `uv run python scripts/build_bundle.py` | Manual / immediate |
| Bundle | Pydantic validation + `bundle.py` | `data/source/*.json` → Python build → `frontend/static/bundle.json` | On every Netlify deploy (~1–2 min from push) |
| Wheel state | Svelte `writable()` store | Store mutation → `localStorage.setItem()` side-effect | On every change (immediate; debounced if needed) |

See [WORKFLOWS.md §3 Build Pipeline](./WORKFLOWS.md#3-build-pipeline) and [WORKFLOWS.md §2 Wheel-State Lifecycle](./WORKFLOWS.md#2-wheel-state-lifecycle) for full diagrams.

---

## Glossary

| Term | Definition |
|------|-----------|
| **scent / flavor / attribute / descriptor** | Synonyms used interchangeably in the codebase and docs. A single perceptual quality associated with an ingredient (e.g. "beany", "meaty", "earthy"). `Scent` is the canonical entity name. |
| **compound / chemical / molecule** | Synonyms for a flavor-active chemical species (e.g. hexanal, 2-acetyl-1-pyrroline). `Compound` is the canonical entity name. |
| **literature / paper(s)** | Synonyms for a bibliographic source — a journal article, review, or book chapter in the `Literature/` folder or referenced via consensus.app. `Citation` is the canonical entity name. |
| **base** | The source ingredient the user is starting from (per-wheel role). Examples: pea protein, soy, mycelium, wheat gluten, faba bean. Role is stored only in Wheel State — not on the Ingredient record. |
| **target** | The product or ingredient the user is trying to taste like (per-wheel role). Examples: beef, chicken, pork, fish, lamb. Same data model as base; role is per-wheel. |
| **on-flavor / off-flavor** | Internal framing only; not surfaced in UI. See the [Problem](#problem) section for why we avoid these labels in user-facing text. |
| **CID** | PubChem Compound Identifier. Integer. The preferred external reference for a Compound record. Optional — some niche compounds lack a PubChem entry. When present, `pubchem_url` is derived at runtime as `https://pubchem.ncbi.nlm.nih.gov/compound/<cid>`. |
| **sensory anchor** | A concrete real-world reference standard for a scent — an object, material, or preparation that exemplifies the attribute. Inspired by the WCR Sensory Lexicon / notbadcoffee.com pattern. No numeric intensity in v1. |
| **MoSCoW** | Prioritization framework: **Must** have (required for v1 success metric), **Should** have (strongly desired; in scope if feasible), **Could** have (nice to have; low priority), **Won't** have (explicitly out of scope for v1). |
| **bundle.json** | The derived, validated JSON artifact written by the Python build pipeline and consumed by the Svelte frontend at app startup. Gitignored; never edited directly. |
| **Wheel State** | The live user session object held in the Svelte store and auto-saved to `localStorage`. Contains ingredient selections, displayed scents, custom scents, color overrides, annotations, and display preferences. Exported/imported as JSON with `schema_version: 1`. |

---

*This is a living document. Update the MoSCoW table status column as capabilities are completed. Last updated: 2026-05-10.*
