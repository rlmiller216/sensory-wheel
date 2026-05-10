# Sensory Wheel Documentation Suite Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce 6 markdown files that codify the v1 spec before any code is written: `README.md`, `CLAUDE.md` (refresh), `docs/PRODUCT_REQUIREMENTS.md`, `docs/SYSTEM_ARCHITECTURE.md`, `docs/WORKFLOWS.md`, `docs/BUSINESS_RULES.md`.

**Architecture:** Files are written in dependency order — schema first (BUSINESS_RULES), then files that reference the schema (SYSTEM_ARCHITECTURE, WORKFLOWS), then files that synthesize across them (PRD, CLAUDE.md), then public-facing summary (README). Each file is reviewed by the spec-document-reviewer subagent before commit. The repo is initialized with git from chunk 1.

**Tech Stack:** Markdown only. Git for version control. No code in this plan.

**Spec source:** [docs/superpowers/specs/2026-05-10-sensory-wheel-docs-design.md](../specs/2026-05-10-sensory-wheel-docs-design.md). All decisions, content outlines, length targets, and cross-document consistency rules live there.

**Working directory:** `/Users/admin/Documents/Claude Projects/Sensory Wheel/`

---

## File map

| Path | Status | Chunk |
|---|---|---|
| `.git/` | TODO — `git init` | 1 |
| `.gitignore` | TODO | 1 |
| `Literature/` | EXISTS | — |
| `docs/superpowers/specs/2026-05-10-sensory-wheel-docs-design.md` | EXISTS | — |
| `docs/superpowers/plans/2026-05-10-sensory-wheel-docs-suite.md` | EXISTS (this file) | — |
| `docs/BUSINESS_RULES.md` | TODO | 2 |
| `docs/SYSTEM_ARCHITECTURE.md` | TODO | 3 |
| `docs/WORKFLOWS.md` | TODO | 4 |
| `docs/PRODUCT_REQUIREMENTS.md` | TODO | 5 |
| `CLAUDE.md` | EXISTS (seed) — REFRESH | 6 |
| `README.md` | TODO | 7 |

---

## Chunk 1: Repo setup

**Files:**
- Create: `.gitignore`
- Initialize: `.git/`

- [ ] **Step 1.1: Initialize git repo**

```bash
cd "/Users/admin/Documents/Claude Projects/Sensory Wheel/"
git init
```

Expected: `Initialized empty Git repository in .../Sensory Wheel/.git/`.

- [ ] **Step 1.2: Create `.gitignore`**

Create `.gitignore` with:

```gitignore
# OS
.DS_Store
Thumbs.db

# Python
__pycache__/
*.pyc
.venv/
.uv-cache/
.pytest_cache/
.ruff_cache/

# uv
# (uv.lock IS committed — do not gitignore it)

# Frontend
frontend/node_modules/
frontend/dist/
frontend/.vite/

# Generated bundle (built by Netlify on every deploy)
frontend/static/bundle.json

# Editor
.vscode/
.idea/
*.swp
*.swo
```

- [ ] **Step 1.3: Verify Literature/ is tracked**

Run: `git status`
Expected: `Literature/` and its 13 PDFs appear under "Untracked files."

`Literature/` is research material; it should be committed so collaborators have the same corpus.

- [ ] **Step 1.4: Stage and commit the initial structure**

```bash
git add .gitignore Literature/ docs/superpowers/specs/ docs/superpowers/plans/ CLAUDE.md
git commit -m "chore: initial commit — research corpus, design spec, implementation plan"
```

Expected: commit succeeds; `git log --oneline` shows one commit.

`CLAUDE.md` is the seed from the prior /init; it will be refreshed in Chunk 6.

---

## Chunk 2: `docs/BUSINESS_RULES.md` (schema authority)

**Files:**
- Create: `docs/BUSINESS_RULES.md` (~400 lines target)

**Purpose:** Single source of truth for every validation, constraint, and guard. Every other doc that mentions a schema field references this file.

- [ ] **Step 2.1: Draft `docs/BUSINESS_RULES.md`**

Follow the spec's §4.6 outline exactly. Use the lab-data-repo `BUSINESS_RULES.md` pattern: **3-layer enforcement legend** (PYD / JS / UI) and per-entity tables.

Structure:

```markdown
# Business Rules

All validation, constraints, and guards enforced across three layers, grouped by entity.

**Layer legend:**
- **PYD** — Pydantic v2 validator at build time. Pydantic IS the schema validator; the bundle is its output.
- **JS** — Frontend guard (Svelte component / store action; runtime imports of wheel-state JSON).
- **UI** — Template-level rendering rule (e.g., plain-text-only for user content).

---

## 1. Scent
### Identity
| Rule | Layer | Enforcement |
| ... |

### Required Fields
| Rule | Layer | Enforcement |
| ... |

### Referential Integrity
| Rule | Layer | Enforcement |
| ... |

(Repeat the same shape for §2 Ingredient, §3 Compound, §4 Citation, §5 Category, §6 Wheel State.)

## 7. Cross-cutting
- Kebab-case slug regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
- `schema_version` exact-match enforcement
- Hex color format
- Soft-delete semantics
- Plain-text rendering rule for user content
```

Each entity table covers: id format, required fields, referential integrity, soft-delete behavior. Pull schema field details from the spec's §3.3.

- [ ] **Step 2.2: Self-review for completeness**

Re-read the file. Confirm every record type from spec §3.3 has a section. Confirm cross-cutting rules at the bottom.

- [ ] **Step 2.3: Dispatch spec-document-reviewer subagent**

Use general-purpose agent with the prompt from [`~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/brainstorming/spec-document-reviewer-prompt.md`](~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.2/skills/brainstorming/spec-document-reviewer-prompt.md), pointed at `docs/BUSINESS_RULES.md`. Provide the spec file path so the reviewer has context for what BUSINESS_RULES.md is supposed to contain.

- [ ] **Step 2.4: Apply reviewer fixes (if any)**

If reviewer returns ❌ Issues Found: fix and re-dispatch. Repeat up to 5 iterations; surface to human if exceeded.

- [ ] **Step 2.5: Commit**

```bash
git add docs/BUSINESS_RULES.md
git commit -m "docs: add BUSINESS_RULES — schema authority"
```

---

## Chunk 3: `docs/SYSTEM_ARCHITECTURE.md`

**Files:**
- Create: `docs/SYSTEM_ARCHITECTURE.md` (~400 lines target)

**Purpose:** Architecture overview. References BUSINESS_RULES.md for schema details rather than redefining.

- [ ] **Step 3.1: Draft `docs/SYSTEM_ARCHITECTURE.md`**

Follow spec §4.4 outline. Sections:

1. Header (Version 0.1.0, Date 2026-05-10, Status Living Document, Scope: static interactive sensory wheel app)
2. Sources synthesized — point to spec, the prior /init plan, the example markdown corpus
3. TOC
4. **System Overview** — single bounded context; tech stack matrix (table from spec §3.1); codebase summary placeholder ("0 LOC, pre-implementation as of 2026-05-10")
5. **Domain Model** — 6 entities (Scent, Ingredient, Compound, Citation, Category, Wheel State). Reference BUSINESS_RULES.md for full field definitions
6. **Source Architecture** — placeholder pointing to `SRC_ARCHITECTURE.md` (to be created after first scaffolding)
7. **Data Model** — JSON-shape diagrams + ERD-style relationship diagram (use ASCII art like the example)
8. Workflows pointer (link to WORKFLOWS.md)
9. Business Rules pointer (link to BUSINESS_RULES.md)
10. **Data Architecture** — build-time pipeline diagram: `data/source/` → Pydantic → `bundle.json` → Vite bundle → Netlify dist
11. **Boundary Contracts** — Python/JS seam (the bundle.json contract); Netlify build contract; browser localStorage contract
12. **Architectural Risks** — bundle size, localStorage cap, Plotly.js sunburst label-density limits, content-curation throughput
13. **Technical Debt & Known Gaps** — initially empty (pre-implementation)

- [ ] **Step 3.2: Self-review**

Re-read. Confirm: tech stack matrix matches spec §3.1; ERD includes all 6 entities; build pipeline diagram shows the 4 stages.

- [ ] **Step 3.3: Dispatch reviewer**

Same pattern as Chunk 2.

- [ ] **Step 3.4: Apply fixes**

- [ ] **Step 3.5: Commit**

```bash
git add docs/SYSTEM_ARCHITECTURE.md
git commit -m "docs: add SYSTEM_ARCHITECTURE — overview, ERD, build pipeline"
```

---

## Chunk 4: `docs/WORKFLOWS.md`

**Files:**
- Create: `docs/WORKFLOWS.md` (~300 lines target)

**Purpose:** State machines and pipelines. References BUSINESS_RULES.md for state-validity rules.

- [ ] **Step 4.1: Draft `docs/WORKFLOWS.md`**

Follow spec §4.5 outline. Sections:

1. Header
2. **Scent Lifecycle State Machine** — `created → active → deprecated`. ASCII diagram. Soft-delete semantics. Triggers and side effects
3. **Wheel-State Lifecycle** — `in-memory → localStorage (auto-save on every change) → JSON export (manual)`. Re-import path. Schema-version mismatch handling
4. **Build Pipeline** — `data/source/*.json` → Pydantic validation → `frontend/static/bundle.json` → Vite build → `frontend/dist/`. Run on every Netlify deploy
5. **Deploy Pipeline** — `git push main` → Netlify build hook → build command → publish `frontend/dist/`. Latency
6. **Curation Workflow** — `Literature/` papers → consensus.app synthesis → hand-edit `data/source/*.json` → `uv run python scripts/build_bundle.py` → `npm run dev` to verify → commit + push
7. **PubChem Fetcher Workflow** — script call → PubChem PUG REST `compound/cid/<CID>/property/...` endpoint → produces a Compound record draft → maintainer pastes into `data/source/compounds.json`. Note: exact URL pattern lives in the script and CLAUDE.md, not here
8. **Retry & Error Handling** — build failures (Pydantic validation surfaced in Netlify logs); deploy failures (rollback procedure); fetcher failures (retry once, fail fast)
9. **Testing Workflow** — Pydantic schema tests at build time; Vitest unit tests for frontend logic; Playwright E2E tests against `npm run dev`

- [ ] **Step 4.2: Self-review**

- [ ] **Step 4.3: Dispatch reviewer**

- [ ] **Step 4.4: Apply fixes**

- [ ] **Step 4.5: Commit**

```bash
git add docs/WORKFLOWS.md
git commit -m "docs: add WORKFLOWS — state machines and pipelines"
```

---

## Chunk 5: `docs/PRODUCT_REQUIREMENTS.md` (the heartbeat)

**Files:**
- Create: `docs/PRODUCT_REQUIREMENTS.md` (~500 lines target)

**Purpose:** MoSCoW-driven feature tracking. Drives implementation priority.

- [ ] **Step 5.1: Draft `docs/PRODUCT_REQUIREMENTS.md`**

Follow spec §4.3 outline. Mirror the lab-data-repo `PRODUCT_REQUIREMENTS.md` shape exactly. Sections:

1. **Header** — Owner: Rebecca Miller. Version: 0.1.0. Last updated: 2026-05-10. Success metric: `% of 5×5 ingredients populated end-to-end + capabilities done`. Current coverage: `0/5 bases populated, 0/5 targets populated, 0/17 capabilities done`. Phrase the counters as "starting state — updates as work lands."
2. **Problem** — plant-based-meat formulation problem in plain language
3. **Vision** — what the tool lets a user do
4. **MoSCoW Status table** — 17 rows from spec §3.4. Status column: all `Not started` for now
5. **Status Definitions & Maintenance Rules** — collapsible `<details>`. Define `Not started / In progress / Bug / Done` evidence requirements; capability-level rollup rules. Refresh scope rules
6. **What's Already Built** — table with one row: "Documentation suite (this folder)"
7. **Capability sections 1–16** — each with: Goal · User story · Feature table (Feature · Priority · Status · Notes) · Known issues · Dependencies. Plotly chart specs in `<details>` blocks for capabilities #1 (WV) and #4 (SP)
8. **Won't (v1)** — table: Texture Domain UI · Comparison Mode · Mobile · i18n · Auth, with reasons
9. **Plotly Chart Conventions** — library version, interactivity, export formats, container class, fixed dimensions, script-loading rules
10. **Architecture Constraints** — load-bearing decisions referenced from CLAUDE.md
11. **Data Flow Reference** — small table: data type · source of truth · sync path · latency
12. **Glossary** — scent / flavor / attribute / descriptor synonyms; on-flavor / off-flavor (internal-only); base; target; CID; etc.

For each capability, write the goal as a single sentence and the user story in classic As a / I want / So that form. Feature tables can be sparse for now (mostly Not-started rows), but every capability must have its row.

- [ ] **Step 5.2: Self-review**

Spot checks: MoSCoW table matches spec §3.4 (17 rows). Each capability section has goal + user story + feature table + dependencies. Glossary is non-empty.

- [ ] **Step 5.3: Dispatch reviewer**

Critical that this file passes review — it's the single most-referenced doc.

- [ ] **Step 5.4: Apply fixes**

- [ ] **Step 5.5: Commit**

```bash
git add docs/PRODUCT_REQUIREMENTS.md
git commit -m "docs: add PRODUCT_REQUIREMENTS — MoSCoW heartbeat"
```

---

## Chunk 6: `CLAUDE.md` (refresh)

**Files:**
- Modify: `CLAUDE.md` (full refresh; current file is the seed from the prior /init)

**Purpose:** AI entry point. Mirror the lab-data-repo `CLAUDE.md` pattern. The current seed CLAUDE.md is too long and doesn't follow the canonical structure.

- [ ] **Step 6.1: Read the current CLAUDE.md**

Run: `Read /Users/admin/Documents/Claude Projects/Sensory Wheel/CLAUDE.md`.

Confirm: it's the seed from the prior /init session (~23 KB). It will be replaced wholesale.

- [ ] **Step 6.2: Draft the refreshed `CLAUDE.md`**

Follow spec §4.2 outline. Mirror lab-data-repo `CLAUDE.md` structure. Sections:

1. **What This Project Is** — one paragraph: static interactive Svelte 5 app for plant-based-meat formulation; Python build-time curation; deployed on Netlify. Live URL placeholder
2. **Before Starting Work** — numbered checklist:
   - Read PRD MoSCoW table (`docs/PRODUCT_REQUIREMENTS.md`, first 50 lines)
   - Read relevant `docs/` for the task — see Architecture Docs table
   - Always read a file before editing
   - Search before creating — default is EDIT, not CREATE
   - Never proactively create .md files without explicit request
3. **Tech Stack** — Python 3.12+, uv, Pydantic v2, Svelte 5, Vite, Plotly.js (slim), jsPDF, html2canvas, Netlify
4. **Architecture Docs** — lookup table: task → which doc. E.g.:
   - "Adding a new ingredient" → `WORKFLOWS.md` §6 Curation
   - "Modifying the schema" → `BUSINESS_RULES.md` §1-7
   - "Understanding data flow" → `SYSTEM_ARCHITECTURE.md` §10 Data Architecture
   - "Starting feature work" → `PRODUCT_REQUIREMENTS.md` MoSCoW table
5. **Project Structure** — annotated tree (Python side `sensory_wheel/`, scripts side `scripts/`, frontend side `frontend/`, content side `data/source/`, research `Literature/`, docs `docs/`)
6. **Coding Style**
   - Python: ruff line-length=100, type hints, Pydantic v2 patterns, kebab-case in IDs only (Python identifiers stay snake_case)
   - Frontend: Prettier + ESLint, Svelte 5 runes (`$state`, `$derived`, `$effect`), TypeScript optional (start with JS, add types later)
7. **Naming Conventions** — kebab-case slugs (`pea-protein`, `cut-grass`), `schema_version: 1`, capability codes
8. **Commit Conventions** — capability codes per spec §3.4 (`feat: wheel renders sunburst (#1-WV)`); searchable audit trail
9. **Commands** — full set from spec §3.1
10. **Data Flow & Ownership** — table: data → source of truth → derivation
11. **How to Extend** — checklists for new ingredient · new scent · new compound · new category · new sensory anchor · new citation
12. **Constraints**
    - Security: plain-text rendering for user content; XSS guard on JSON imports; no remote calls in deployed app
    - Architecture: build-time bundle only — no live scraping; `data/source/` is truth
    - UI: Plotly.js loaded once; sunburst is the only chart type
13. **Load-Bearing Decisions** — soft-delete semantics, kebab-case slugs, build-time bundle, schema_version exact-match, plain-text rendering

- [ ] **Step 6.3: Replace `CLAUDE.md` wholesale**

Use `Write` tool — overwrites the seed file.

- [ ] **Step 6.4: Self-review**

Spot checks: Architecture Docs table covers the 4 task types. Project Structure tree includes `Literature/`. How to Extend has a checklist for each entity.

- [ ] **Step 6.5: Dispatch reviewer**

- [ ] **Step 6.6: Apply fixes**

- [ ] **Step 6.7: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: refresh CLAUDE.md — mirror lab-data-repo project-rules pattern"
```

---

## Chunk 7: `README.md` (public-facing)

**Files:**
- Create: `README.md` (~200 lines target)

**Purpose:** Public front door on GitHub. First thing visitors see.

- [ ] **Step 7.1: Draft `README.md`**

Follow spec §4.1 outline. Sections:

1. **Hero** — H1 (`# Sensory Wheel`), 1-line tagline ("Interactive sunburst chart for plant-based-meat flavor formulation"), placeholder for hero screenshot/GIF (`![Sensory Wheel demo](docs/images/hero.png)` — image to be added later)
2. **What it is** — one paragraph
3. **Why** — the plant-based-meat formulation problem in plain language. Mention bases (pea, soy, mycelium, wheat gluten, faba bean) vs targets (beef, chicken, pork, fish, lamb)
4. **Live demo** — link placeholder (`[Live demo →](https://sensory-wheel.netlify.app)` — actual URL added after deploy)
5. **Tech stack** — bulleted: Svelte 5 (Vite), Plotly.js, Python (uv) for curation, Pydantic v2, Netlify
6. **Quick start**
   ```bash
   git clone https://github.com/<user>/sensory-wheel
   cd sensory-wheel
   uv sync
   uv run python scripts/build_bundle.py
   cd frontend && npm install && npm run dev
   ```
7. **Project structure** — small annotated tree (top level only — `data/`, `frontend/`, `sensory_wheel/`, `scripts/`, `docs/`, `Literature/`)
8. **Documentation** — bulleted links to:
   - `CLAUDE.md` — for AI sessions
   - `docs/PRODUCT_REQUIREMENTS.md` — MoSCoW heartbeat
   - `docs/SYSTEM_ARCHITECTURE.md` — overview
   - `docs/WORKFLOWS.md` — pipelines
   - `docs/BUSINESS_RULES.md` — schema authority
9. **License** — MIT, with one-line notice
10. **Credits** — FlavorDB2 (IIIT Delhi), TGSC (The Good Scents Company), PubChem (NIH NLM), `consensus.app`, the 13 paper authors in `Literature/` (link to a list inside the README or to the citation file)

- [ ] **Step 7.2: Self-review**

Spot checks: live demo link present (placeholder OK); quick start commands match the actual stack; documentation links match the 5 created docs.

- [ ] **Step 7.3: Dispatch reviewer**

- [ ] **Step 7.4: Apply fixes**

- [ ] **Step 7.5: Commit**

```bash
git add README.md
git commit -m "docs: add README — public-facing front door"
```

---

## Chunk 8: Cross-document consistency pass + final review

**Files:**
- Read all 6 markdown files for cross-checking
- Modify any that have inconsistencies

**Purpose:** Enforce spec §5 cross-document consistency rules.

- [ ] **Step 8.1: Run cross-document consistency check**

Read all 6 files. Verify:

1. Schema fields are defined ONCE — only in `BUSINESS_RULES.md`. Other files reference it.
2. Capability codes (`#1-WV`, `#2-IP`, …) are consistent everywhere they appear (PRD, CLAUDE.md commit conventions, possibly WORKFLOWS).
3. Status values in the PRD are `Not started` everywhere (no code yet).
4. Cross-references use markdown links, not "see the other doc" prose.
5. No file exceeds its length target by >50%.

- [ ] **Step 8.2: Apply consistency fixes**

If any rule is violated, fix it. Common fixes:
- Schema field redefined in SYSTEM_ARCHITECTURE → replace with link to `BUSINESS_RULES.md#section`.
- Capability code typo (`#1-WV` vs `#1-WL`) → unify on the canonical code from spec §3.4.

- [ ] **Step 8.3: Dispatch full-suite reviewer**

Dispatch one final spec-document-reviewer pass on the full set, providing:
- All 6 file paths
- The spec at `docs/superpowers/specs/2026-05-10-sensory-wheel-docs-design.md`
- Spec §5 cross-document rules

Reviewer should treat the suite as a single artifact and verify cross-document consistency.

- [ ] **Step 8.4: Apply final fixes**

- [ ] **Step 8.5: Final commit**

```bash
git add -A
git commit -m "docs: cross-document consistency pass — all 6 files reviewed"
```

- [ ] **Step 8.6: Optional — push to GitHub**

If a GitHub repo has been created (out of scope for this plan), push:

```bash
git remote add origin https://github.com/<user>/sensory-wheel.git
git push -u origin main
```

---

## Definition of done for this plan

- All 6 markdown files exist at the paths in the file map.
- Each file has been reviewed by spec-document-reviewer and approved.
- The cross-document consistency pass (Chunk 8) has been completed.
- All commits are made; `git log --oneline` shows the documentation work.
- Maintainer (Rebecca) has not yet been asked to review — that's the next handoff after this plan completes.

---

## What this plan does NOT cover

These are deliberately out of scope; they belong in a follow-up plan:

- Scaffolding any code (`uv init`, `npm create vite`, etc.)
- Writing any source files (`schemas.py`, Svelte components, etc.)
- Curating any content (populating `data/source/*.json`)
- Setting up Netlify deployment
- Writing `SRC_ARCHITECTURE.md` (deferred until first scaffolding lands)

After this plan completes, the next phase should be a **scaffolding plan** that uses the docs as input.
