# Sensory Wheel — Workflows, State Machines & Pipelines

> **Version**: 0.1.0
> **Date**: 2026-05-10
> **Status**: Living Document
> **Scope**: Workflows, state machines, pipelines for Sensory Wheel v1

This document describes how work flows through the system: entity lifecycles, build and deploy pipelines, the maintainer curation workflow, PubChem fetcher usage, error handling, and the testing workflow.

Cross-references:
- [BUSINESS_RULES.md](./BUSINESS_RULES.md) — schema authority; state-validity rules per entity
- [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) — layer boundaries (§7 Data Architecture, §8 Boundary Contracts)

---

## Table of Contents

1. [Scent Lifecycle State Machine](#1-scent-lifecycle-state-machine)
2. [Wheel-State Lifecycle](#2-wheel-state-lifecycle)
3. [Build Pipeline](#3-build-pipeline)
4. [Deploy Pipeline](#4-deploy-pipeline)
5. [Curation Workflow](#5-curation-workflow)
6. [PubChem Fetcher Workflow](#6-pubchem-fetcher-workflow)
7. [Retry & Error Handling](#7-retry--error-handling)
8. [Testing Workflow](#8-testing-workflow)

---

## 1. Scent Lifecycle State Machine

All curated records (Scent, Ingredient, Compound, Citation, Category) follow the same soft-delete pattern, but the Scent record is the most consequential because it drives every wheel display.

### State diagram

```
  Maintainer creates record in data/source/scents.json
                     │
                     ▼
              ┌─────────────┐
              │   created   │  ← initial state on first hand-edit
              └──────┬──────┘
                     │  build runs; Pydantic validates; record enters bundle.json
                     ▼
              ┌─────────────┐
              │   active    │  ← deprecated: false (default)
              └──────┬──────┘
                     │  maintainer sets deprecated: true in scents.json
                     ▼
              ┌─────────────┐
              │ deprecated  │  ← soft-deleted; record stays in JSON forever
              └─────────────┘
```

### States

| State | `deprecated` value | Meaning |
|-------|-------------------|---------|
| `created` | `false` | Record has been added to `data/source/scents.json` but not yet validated by a successful build. Transient — exists only between a hand-edit and the next build run. |
| `active` | `false` | Record passed Pydantic validation, exists in `bundle.json`, and is rendered in the wheel by the frontend. |
| `deprecated` | `true` | Record is soft-deleted. Still present in `data/source/scents.json` and `bundle.json`; never hard-deleted. |

### Soft-delete semantics

Hard deletion of any curated record is **prohibited**. Files never shrink. A Scent record set to `deprecated: true`:

- Remains in `data/source/scents.json` and passes through into `bundle.json` unchanged.
- Is **excluded from wheel rendering** — `data.js` filters out deprecated scents before building the Plotly figure.
- Is **included in past wheel exports** — old JSON exports continue to reference it. On re-import, the frontend warns ("this wheel references deprecated scents") but does not reject the file.

See [BUSINESS_RULES.md §7 — Soft-Delete Semantics](./BUSINESS_RULES.md#soft-delete-semantics) for the cross-entity definition of this rule.

### Trigger

The maintainer hand-edits `data/source/scents.json` (or any other source file). This is the only write path — no automated process mutates the source files.

### Side effects on state change

| Transition | Side effects |
|---|---|
| `created → active` | Build re-runs (manually or via `git push`). Netlify deploys updated `bundle.json`. App serves the new scent. |
| `active → deprecated` | Build re-runs. New `bundle.json` marks the scent deprecated. Frontend excludes it from new wheels. Any already-saved wheel state that references the scent displays a warning on next import. |

---

## 2. Wheel-State Lifecycle

The wheel state is the user's live session object. It is not a curated-data file — it is never written to `data/source/`. Its lifecycle spans three storage layers.

### State diagram

```
  App loads (first visit, or localStorage empty)
                     │
                     ▼
          ┌──────────────────────┐
          │  in-memory           │  ← Svelte writable() store; default wheel state
          │  (Svelte store)      │
          └──────────┬───────────┘
                     │  on every store mutation (subscribe → setItem)
                     ▼
          ┌──────────────────────┐
          │  localStorage        │  ← auto-saved; key: sensory_wheel_state
          │  (auto-save)         │
          └──────────┬───────────┘
                     │  user clicks "Export JSON"
                     ▼
          ┌──────────────────────┐
          │  JSON export         │  ← downloaded file; manual user action
          │  (manual)            │
          └──────────────────────┘
```

### Phases

| Phase | How it works |
|-------|--------------|
| **In-memory** | Svelte `writable()` store. Initialized from `localStorage` on app load, or from a default object on first visit. Every mutation (pick ingredient, remove scent, edit annotation) updates the store. |
| **localStorage** | `subscribe()` side-effect calls `setItem('sensory_wheel_state', JSON.stringify(state))` on every mutation. Cap: ~1 MB per wheel. Exceeding the cap prompts the user to export and clear. `QuotaExceededError` degrades gracefully — see [§7](#7-retry--error-handling). |
| **JSON export** | User downloads current wheel state as `.json`. Complete snapshot; always contains `schema_version: 1` and `app_version`. Can be re-imported to recreate the wheel exactly. |

### Re-import path

```
  User selects file via file picker
            │
            ▼
  JSON.parse() in try/catch
    └─ parse failure → user-facing error; state unchanged; abort
            │
            ▼
  JS type guard: structural validation
    └─ invalid shape → user-facing error; state unchanged; abort
            │
            ▼
  schema_version check: must equal 1 exactly
    └─ mismatch → fail loudly ("expected 1, got <actual>"); refuse to load
       See BUSINESS_RULES.md §6 and §7 (Schema Version)
            │
            ▼
  app_version logged; no compatibility enforcement on app_version
            │
            ▼
  Resolve ingredient_ids, scent IDs against bundle.json
    └─ unresolvable or deprecated refs → non-blocking warning; load continues
            │
            ▼
  store.set(validatedState)
  localStorage updated immediately via subscribe side-effect
```

Schema-version mismatch is a hard stop — the app never silently upgrades an incompatible wheel state. This is enforced in the JS layer per [BUSINESS_RULES.md §6 — Wheel State](./BUSINESS_RULES.md#6-wheel-state) and the cross-cutting [Schema Version rule](./BUSINESS_RULES.md#schema-version).

---

## 3. Build Pipeline

The build pipeline runs at deploy time (and locally when the maintainer runs `scripts/build_bundle.py` to verify changes). It transforms hand-edited source JSON into a validated, frontend-ready bundle.

### Pipeline diagram

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
```

This diagram matches [SYSTEM_ARCHITECTURE.md §7.1](./SYSTEM_ARCHITECTURE.md#71-build-time-pipeline) exactly — the architecture doc is the canonical home for the full data-flow context.

### Failure mode

A Pydantic `ValidationError` in `load.py` causes `scripts/build_bundle.py` to exit with a non-zero code. This aborts the entire pipeline: `bundle.json` is not written, the Vite build does not run, and the Netlify deploy does not publish. The error message (naming the failing entity and field) appears in the Netlify build log. The previous successful deploy remains live.

---

## 4. Deploy Pipeline

Every push to `main` triggers an automatic Netlify deploy. The deploy wraps the full build pipeline.

### Pipeline diagram

```
  git push origin main
          │
          ▼
  Netlify webhook fires
          │
          ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │  Netlify build environment                                        │
  │                                                                   │
  │  uv sync                          ← install Python deps          │
  │    │                                                              │
  │    ▼                                                              │
  │  uv run python scripts/build_bundle.py                           │
  │    │   ← Pydantic validates data/source/*.json                   │
  │    │   ← writes frontend/static/bundle.json                      │
  │    │   ← exits non-zero on any validation failure → ABORT        │
  │    ▼                                                              │
  │  cd frontend && npm install && npm run build                      │
  │    │   ← Vite bundles Svelte app + bundle.json                   │
  │    │   ← writes frontend/dist/                                   │
  │    ▼                                                              │
  │  Netlify publishes frontend/dist/  (atomic swap)                 │
  └──────────────────────────────────────────────────────────────────┘
          │
          ▼
  Live site updated (~1–2 minutes from push)
```

### Build command (configured in `netlify.toml`)

```
uv sync && uv run python scripts/build_bundle.py && cd frontend && npm install && npm run build
```

**Publish directory**: `frontend/dist/`

### Latency

Typical deploy time from `git push` to live site: **~1–2 minutes** (dominated by `npm install` and the Vite build; Python validation adds a few seconds).

### Rollback procedure

Two options, in preference order:

1. **Revert commit on main** — `git revert <bad-commit>` (or `git reset` if the commit hasn't been pushed and shared). Push the revert to `main`; Netlify rebuilds automatically from the reverted state. This is the preferred approach because it keeps `main` as the source of truth.

2. **Netlify "Restore deploy" UI** — navigate to the Netlify site dashboard → Deploys → select a known-good prior deploy → click "Publish deploy." This rolls forward to a previously-built artifact without requiring a new git commit. Use this when a quick hotfix is needed before the git revert is ready, or when the build environment itself is broken.

---

## 5. Curation Workflow

The maintainer's day-to-day process for adding or updating curated content. This is the human workflow that feeds the build pipeline.

### Steps (in order)

```
  1. Read papers in Literature/
          │
          │  Primary corpus: 13 PDFs on meat/fish/poultry flavor + analogue texture
          ▼
  2. Synthesize via consensus.app
          │
          │  Cross-paper insights: "what are the defining flavor attributes of beef?"
          │  Produces a curated list of scent descriptors per ingredient
          ▼
  3. Hand-edit data/source/*.json
          │
          │  Files edited in any order as needed:
          │    taxonomy.json    ← add/modify category nodes
          │    scents.json      ← add/modify Scent records
          │    compounds.json   ← add/modify Compound records (use fetcher for CID lookup)
          │    citations.json   ← add structured citation records from papers
          │    ingredients.json ← add/modify Ingredient records + their scent lists
          │
          │  Conventions:
          │    • All IDs are kebab-case slugs
          │    • Set deprecated: true instead of deleting records
          │    • See BUSINESS_RULES.md for per-entity field rules
          ▼
  4. Run uv run python scripts/build_bundle.py
          │
          │  Validates edits via Pydantic; builds bundle.json
          │  Fix any validation errors and re-run until clean
          ▼
  5. Run npm run dev (in frontend/)
          │
          │  Verify in the browser: wheel renders, side panel shows expected data,
          │  no console errors, deprecated scents excluded from display
          ▼
  6. git commit + git push origin main
          │
          │  Netlify auto-deploys (see §4)
          ▼
  Live site updated
```

---

## 6. PubChem Fetcher Workflow

A maintainer-side helper script that automates the most tedious part of compound curation. It is never deployed and never called by the browser.

### Trigger

```bash
uv run python scripts/fetch_compound.py <CID>
```

Where `<CID>` is a PubChem Compound Identifier (integer), looked up manually by the maintainer on [pubchem.ncbi.nlm.nih.gov](https://pubchem.ncbi.nlm.nih.gov).

### Workflow

```
  Maintainer finds a CID on PubChem
          │
          ▼
  uv run python scripts/fetch_compound.py <CID>
          │
          ▼
  Script calls PubChem PUG REST
  compound/cid/<CID>/property/... endpoint
          │
          │  Retrieves: preferred name, IUPAC name, molecular formula,
          │             connectivity SMILES, synonyms
          ▼
  Script outputs a Compound record draft (JSON)
  ── printed to stdout ──────────────────────────────────
  {
    "id": "<slug-to-fill-in>",
    "name": "...",
    "cid": <CID>,
    "synonyms": [...],
    "cas_number": null,
    "smiles": "...",
    "formula": "...",
    "flavordb_url": null,
    "deprecated": false
  }
  ───────────────────────────────────────────────────────
          │
          ▼
  Maintainer reviews, assigns a kebab-case slug id,
  pastes record into data/source/compounds.json
          │
          ▼
  Run build_bundle.py to validate + regenerate bundle
```

The exact URL pattern used by the fetcher script is documented inside `scripts/fetch_compound.py` and in [CLAUDE.md](../CLAUDE.md). It is not pinned here because the PubChem API surface is maintained by NCBI and the script is the authoritative reference.

### Failure handling

See [§7 — Fetcher failures](#fetcher-failures).

---

## 7. Retry & Error Handling

Each failure mode is paired with its detection point and recovery approach.

### Build failures

**Trigger**: A Pydantic `ValidationError` in `sensory_wheel/load.py`, or a referential integrity error (e.g., a Scent references a Compound ID that does not exist in `compounds.json`).

**Detection**: `scripts/build_bundle.py` exits non-zero. Error message names the failing entity and field.

**Where surfaced**: Netlify build log (on `git push`), or terminal output (on local run).

**Recovery**: Fix the validation error in the relevant `data/source/*.json` file and re-run `uv run python scripts/build_bundle.py`. Once the build is clean, commit and push.

**Deploy impact**: The deploy aborts before any new artifact is published. The previous successful deploy remains live. The `main` branch is unchanged (the push succeeded; only the Netlify build failed).

### Deploy failures

**Trigger**: Any non-zero exit from any step in the Netlify build command.

**Detection**: Netlify build log shows the failed command and exit code.

**Recovery**: See [§4 — Rollback procedure](#rollback-procedure). Either revert the commit on `main` (preferred), or use Netlify's "Restore deploy" UI to serve a known-good prior artifact while the fix is prepared.

### Fetcher failures

The PubChem fetcher (`scripts/fetch_compound.py`) is a maintainer-side CLI tool. It does not affect the deployed app.

| Error | Behavior |
|-------|----------|
| HTTP 429 (rate limited) or 5xx (server error) | Retry once after a short delay. If the retry also fails, exit with a clear error message and instructions to try again later. |
| HTTP 404 (CID does not exist) | Fail fast — no retry. The CID is invalid. Exit immediately with "CID `<n>` not found on PubChem." |
| Network timeout or unreachable | Fail fast with a clear error. The deployed app is never affected — it reads only from `bundle.json` and never calls PubChem. |

### localStorage write failures

**Trigger**: Browser `localStorage` quota exceeded (throws `QuotaExceededError` from `setItem()`), or `localStorage` is disabled by the browser.

**Detection**: `try/catch` around `localStorage.setItem()` in `store.js`.

**Behavior**: The app degrades gracefully — state is maintained in-memory only. A persistent banner informs the user: "Auto-save is off — export your wheel to preserve it." The user can continue using the app and export their wheel state at any time. The app does not crash.

This matches the ~1 MB per-wheel size cap enforced by `store.js` before each write — see [BUSINESS_RULES.md §6 — Storage](./BUSINESS_RULES.md#storage) and [SYSTEM_ARCHITECTURE.md §8.3](./SYSTEM_ARCHITECTURE.md#83-browser-localstorage-contract).

---

## 8. Testing Workflow

Three testing layers cover the Python build pipeline, frontend logic, and end-to-end user flows.

| Layer | Command | Scope | When to run |
|-------|---------|-------|-------------|
| **Pydantic schema tests** | `uv run pytest tests/` | Validates each model, referential integrity, reverse indexes, `bundle.json` shape | Before every commit touching `data/source/*.json` or `sensory_wheel/` |
| **Vitest unit tests** | `cd frontend && npm run test` | `data.js` lookups, `wheel.js` sunburst builder, `store.js` import type guard, color resolution precedence | Before every commit touching `frontend/src/` |
| **Playwright E2E tests** | `cd frontend && npm run e2e` | Full user flows: pick ingredient → wheel renders; click wedge → side panel opens; export/import round-trip; schema_version rejection; localStorage persistence | Before every pull request or deploy to `main` |

Playwright prerequisite: `bundle.json` must exist (`uv run python scripts/build_bundle.py`). The Vite dev server is started automatically by the Playwright config.

---

*This file was created during the docs-first phase (2026-05-10). Update §3 Build Pipeline and §4 Deploy Pipeline if the Netlify build command or publish directory changes. Update §8 Testing Workflow as the test suite is built out.*
