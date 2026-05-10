# CLAUDE.md — Project Rules

## What This Project Is

Sensory Wheel is a static interactive Svelte 5 app for plant-based-meat flavor formulation. A Python build-time pipeline curates JSON records (scents, compounds, ingredients, citations, taxonomy) and bundles them into a single `bundle.json` that Netlify serves alongside the compiled frontend. The user picks base and target ingredients, sees their associated scents rendered as a multi-layer Plotly.js sunburst chart, and can click any wedge for compound and citation detail. Live at `https://sensory-wheel.netlify.app/` (URL to be confirmed at deploy time — see [docs/WORKFLOWS.md](./docs/WORKFLOWS.md) §4 Deploy Pipeline).

---

## Before Starting Work

1. Read the PRD MoSCoW table ([`docs/PRODUCT_REQUIREMENTS.md`](./docs/PRODUCT_REQUIREMENTS.md), first 50 lines) for current capability status.
2. Read relevant `docs/` for architecture changes — see Architecture Docs table below.
3. Always read a file before editing it.
4. Search before creating — default is EDIT, not CREATE.
5. Never proactively create `.md` files unless explicitly requested.
6. Starting capability work? Read the PRD MoSCoW table, then the specific capability section, then verify status against the current codebase before coding.

---

## Tech Stack

- Python 3.12+, `uv` (package manager — never `pip` or `poetry`)
- Pydantic v2 (build-time schema validation; violations abort the build)
- Svelte 5 (with Vite) for the frontend
- Plotly.js (`plotly.js-strict-dist-min` slim build) for the sunburst chart
- jsPDF + html2canvas for in-browser PDF export
- Netlify (static hosting — no server, no cold starts)
- Single-language (English), single-user, desktop-first (≥1024 px)

---

## Architecture Docs

The entry point for AI sessions. Find the task, read the doc listed.

| Task | Read first |
|---|---|
| Adding/modifying a schema field | [`docs/BUSINESS_RULES.md`](./docs/BUSINESS_RULES.md) §1–§7 |
| Adding a new ingredient | [`docs/WORKFLOWS.md`](./docs/WORKFLOWS.md) §5 Curation Workflow |
| Modifying the build pipeline | [`docs/SYSTEM_ARCHITECTURE.md`](./docs/SYSTEM_ARCHITECTURE.md) §7, [`docs/WORKFLOWS.md`](./docs/WORKFLOWS.md) §3 |
| Understanding overall system | [`docs/SYSTEM_ARCHITECTURE.md`](./docs/SYSTEM_ARCHITECTURE.md) §1–§4 |
| Deploying to Netlify | [`docs/WORKFLOWS.md`](./docs/WORKFLOWS.md) §4 Deploy Pipeline |
| Starting feature or bugfix work | [`docs/PRODUCT_REQUIREMENTS.md`](./docs/PRODUCT_REQUIREMENTS.md) — MoSCoW table |
| Adding a state machine or workflow | [`docs/WORKFLOWS.md`](./docs/WORKFLOWS.md) |

---

## Project Structure

```
sensory_wheel/    → Python package — schemas, load, bundle. Build-time only.
scripts/          → Python entrypoints (build_bundle, fetch_compound).
data/source/      → Curated JSON, hand-edited. The source of truth.
frontend/         → Svelte 5 app. The deployed thing.
tests/            → Python tests (pytest).
docs/             → BUSINESS_RULES, SYSTEM_ARCHITECTURE, WORKFLOWS, PRD.
Literature/       → Maintainer's research PDFs (not app data).
```

---

## Coding Style

**Python:**
- ruff, line-length=100
- `from __future__ import annotations` in every file
- Type hints everywhere
- Pydantic v2 patterns for all schema models
- IDs in data are kebab-case slugs; Python identifiers stay snake_case

**Frontend:**
- Prettier + ESLint
- Svelte 5 runes (`$state`, `$derived`, `$effect`)
- TypeScript is optional — start with JS, add types later if useful

**Security (both layers):**
- All user-supplied text renders as plain text — no `{@html}`, no Markdown rendering, no innerHTML. This is the XSS guard for imported wheel-state JSON.

---

## Naming Conventions

- All entity IDs: kebab-case slugs (`pea-protein`, `cut-grass`, `2-acetyl-1-pyrroline`)
- `schema_version: 1` exact match on every JSON file (increment only on breaking changes)
- Capability codes: WV, IP, SM, SP, HD, LS, IO, CD, CN, CC, CS, DT, DL, AN, AC, RM (see [`docs/PRODUCT_REQUIREMENTS.md`](./docs/PRODUCT_REQUIREMENTS.md#moscow-status) MoSCoW table)

---

## Commit Conventions

Conventional Commits format: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`

When a commit affects a PRD capability, include the capability number and code:

```
feat: render sunburst from bundle (#1-WV)
fix: resolve color override conflict (#10-CC)
docs: clarify soft-delete in BUSINESS_RULES (#-)
```

Searchable audit trail: `git log --oneline --grep="#1-WV"`

---

## Commands

```bash
# Python (build-time curation)
uv sync                                         # install deps
uv add <pkg>                                    # add dep
uv run python scripts/build_bundle.py           # regenerate bundle
uv run python scripts/fetch_compound.py <CID>   # PubChem helper
uv run pytest tests/ -v                         # run tests

# Frontend (the deployed app)
cd frontend
npm install
npm run dev          # Vite dev server
npm run build        # production build
npm run preview      # preview production build
npm run test         # Vitest unit tests
npm run e2e          # Playwright E2E tests
```

Before committing: run `uv run pytest && cd frontend && npm run test`. If the commit affects a PRD capability, update [`docs/PRODUCT_REQUIREMENTS.md`](./docs/PRODUCT_REQUIREMENTS.md) — see the PRD's Status Definitions section.

---

## Data Flow & Ownership

| Data | Source of truth | Sync path | Frequency |
|---|---|---|---|
| Curated records | Maintainer | Hand-edited in `data/source/*.json` | On commit |
| Bundle | Python build | `uv run python scripts/build_bundle.py` → `frontend/static/bundle.json` | On every Netlify deploy |
| Wheel state | User session | Svelte writable store ↔ browser localStorage | On every change |

---

## How to Extend

**New ingredient:**
1. Add to `data/source/ingredients.json` with kebab-case `id` and the `scents` list
2. Run `uv run python scripts/build_bundle.py` to regenerate
3. `npm run dev` to verify the ingredient picker shows it

**New scent:**
1. Add to `data/source/scents.json` — see [`docs/BUSINESS_RULES.md`](./docs/BUSINESS_RULES.md#1-scent) §1 for required vs. optional fields
2. Ensure `category_ids` and `compounds` (if any) all resolve to existing IDs
3. Build + verify

**New compound:**
1. Optional: `uv run python scripts/fetch_compound.py <CID>` to draft the record from PubChem
2. Paste into `data/source/compounds.json`
3. Build + verify

**New category:**
1. Add to `data/source/taxonomy.json` with `id`, `name`, `parent_id` (or null for top-level), optional `default_color`
2. Build + verify

**New sensory anchor (a real-world reference standard for a scent):**
1. Find the relevant scent record in `data/source/scents.json`
2. Append to its `sensory_anchors` array: `{name, modality: "aroma" | "flavor", preparation_notes?}` — see [`docs/BUSINESS_RULES.md`](./docs/BUSINESS_RULES.md#1-scent) §1 for the full shape
3. Build + verify

**New capability:**
1. Add a row to the PRD MoSCoW table with the next `#N` + a 2-letter code
2. Add a `## N. Capability Name (CODE)` section with Goal / User Story / Feature table / Known issues / Dependencies
3. Update the Architecture Docs table in `CLAUDE.md` if a new doc is needed

---

## Constraints

**Security:**
- All user-supplied text renders as plain text (no Markdown, no `{@html}`, no innerHTML)
- No remote calls from the deployed app — the only network activity is loading `bundle.json` from the same origin
- Imported wheel-state JSON is validated structurally before any state mutation

**Architecture:**
- `data/source/*.json` is the source of truth; `bundle.json` is derived (gitignored, regenerated by Netlify)
- No live scraping of PubChem / FlavorDB / TGSC at runtime
- `fetch_compound.py` is a maintainer-side helper only — never called from the deployed app

**UI:**
- Plotly.js is loaded once (slim `plotly.js-strict-dist-min` build); the sunburst is the only chart type for v1
- Layout is desktop-first (≥1024 px); mobile is out of v1 scope

---

## Load-Bearing Decisions

- `data/source/` is truth; `bundle.json` is derived — never commit `bundle.json`
- All entity IDs are kebab-case slugs; renames are explicit migrations
- `schema_version` exact-match on every JSON file
- Soft-delete via `deprecated: true` — records are never hard-deleted; past wheel exports keep resolving
- Plain-text rendering for all user-supplied text (XSS guard)
- Build-time bundle — no runtime data fetches in the deployed app
- On-flavor / off-flavor framing is INTERNAL only — never surface these labels in the UI
