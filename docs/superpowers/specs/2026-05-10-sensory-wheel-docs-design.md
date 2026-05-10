# Sensory Wheel — Documentation Suite v1: Design Spec

**Status**: Draft for review
**Date**: 2026-05-10
**Author**: Rebecca Miller (with Claude Code)
**Phase**: Spec → docs (no code yet)
**Next phase**: Implementation plan via `superpowers:writing-plans`

---

## 1. Context

The Sensory Wheel project is a static interactive web app that visualizes the flavor / aroma landscape of plant-based-meat formulation. The user picks one or more **base** ingredients (e.g. pea protein, soy) and one or more **target** ingredients (e.g. beef, lamb); the app renders a multi-layer sunburst showing the union of associated scents organized by a curated taxonomy.

The previous /init session produced a seed `CLAUDE.md` capturing the locked-in spec from a multi-round Q&A. This session extends that spec into a **documentation suite** to be written **before any code lands**.

The example markdown files at `~/Desktop/Example Markdown Files/` (from the maintainer's `lab-data-repo` project) provide proven structures to co-opt: PRD, CLAUDE.md, SYSTEM_ARCHITECTURE, WORKFLOWS, BUSINESS_RULES, MEMORY_ARCHITECTURE, SRC_ARCHITECTURE.

---

## 2. Goal

Produce **6 markdown files** that together codify the v1 spec. The files are the deliverable for this phase; code/scaffolding follows in a separate phase via `writing-plans`.

The 6 files:

```
Sensory Wheel/
├── README.md                       # public-facing front door
├── CLAUDE.md                       # AI rules (REFRESH the seed from the prior /init)
├── docs/
│   ├── PRODUCT_REQUIREMENTS.md     # MoSCoW heartbeat
│   ├── SYSTEM_ARCHITECTURE.md      # tech stack, ERD, build pipeline
│   ├── WORKFLOWS.md                # pipelines + state machines
│   └── BUSINESS_RULES.md           # validation rules per entity
└── Literature/                     # already exists (13 PDFs)
```

`SRC_ARCHITECTURE.md` and `MEMORY_ARCHITECTURE.md` are deliberately deferred. SRC_ARCHITECTURE can't be written before code exists; MEMORY_ARCHITECTURE is overkill for a single-author personal portfolio app.

---

## 3. Locked-in decisions (the input to the docs)

These were resolved across 12 brainstorming questions in this session and the previous /init session.

### 3.1 Stack

| Area | Decision |
|---|---|
| Architecture | Static frontend + build-time Python curation. No server, no cold starts. |
| Frontend framework | Svelte 5 (with Vite) |
| Visualization | Plotly.js `sunburst` (slim `plotly.js-strict-dist-min` build, ~800 KB) |
| Curation language | Python, managed by `uv` |
| Schema validation | Pydantic v2 at build time |
| In-browser PDF | jsPDF + html2canvas |
| State management | Single Svelte `writable()` store, auto-synced to `localStorage` |
| Hosting | Netlify (static) |
| Build timing | At Netlify build time. `bundle.json` is gitignored. `data/source/*.json` is the only truth. |
| Repo + license | Public GitHub repo, MIT license |
| Version control | Git from day 1 |

### 3.2 Product

| Area | Decision |
|---|---|
| Audience | Public + interactive. First-load shows pre-populated demo: **soy (base) + beef (target)**. |
| Success metric | Live deployed demo with **5 bases × 5 targets** populated end-to-end (scents + compounds + citations). Visitor can pick base + target, see wheel, click for detail, export PDF. |
| 5 bases | pea protein, soy, mycelium, wheat gluten, faba bean |
| 5 targets | beef, chicken, pork, fish, lamb |
| Top-level taxonomy | Aromatic family: Floral, Fruity, Vegetal, Roasted, Spicy, Animal, Mineral, Off-notes |
| Primary research corpus | `Literature/` folder + <https://consensus.app> for synthesis |

### 3.3 Schema (recap from prior /init)

- Single curated JSON shape with `domain: "scent" \| "texture"` (textures schema-ready, UI deferred).
- `compound_id` slug is the universal key; PubChem `cid` is preferred-but-optional.
- All IDs are kebab-case slugs (`cut-grass`, `pea-protein`).
- Every record carries `deprecated: bool` (soft-delete; files never shrink).
- Every JSON file (curated + exported wheel state) starts with `schema_version: 1`. Wheel-state JSON also carries `app_version`.
- Multi-category scents: `Scent.category_ids: list[str]` (a scent may belong to multiple categories).
- Forward lists in JSON; reverse indexes built at app startup. No junction files on disk.
- Citations: structured (`title, authors, year, doi, url, journal, volume, pages, publisher, source_kind, local_pdf_filename`).
- Sensory anchors: `{name, modality: "aroma" | "flavor", preparation_notes?}`. No numeric intensity.
- Color resolution precedence: per-scent override > `Scent.default_color` > category `default_color`.
- Definitions are user-authored; TGSC/FlavorDB are *maintainer* research inputs only.
- Plain-text rendering for all user-supplied content (XSS guard on JSON imports).

### 3.4 Capability list (the PRD's MoSCoW table)

| # | Code | Capability | Priority |
|---|---|---|---|
| 1 | WV | Wheel Visualization | Must |
| 2 | IP | Ingredient Picker | Must |
| 3 | SM | Scent Management Sidebar | Must |
| 4 | SP | Side Panel Detail View | Must |
| 5 | HD | Hierarchy Depth Control | Must |
| 6 | LS | localStorage Persistence | Must |
| 7 | IO | JSON Import/Export | Must |
| 8 | CD | Curation Data Pipeline | Must |
| 9 | CN | Curated Content (5×5 ingredients) | Must |
| 10 | CC | Color Customization | Should |
| 11 | CS | Custom Free-text Scents | Should |
| 12 | DT | Definitions Toggle | Should |
| 13 | DL | Multi-format Download (SVG/PNG/PDF) | Should |
| 14 | AN | Per-wheel Annotations | Should |
| 15 | AC | Accessibility Fallback (a11y data table) | Could |
| 16 | RM | README Polish | Could |
| 17 | — | Won't (v1): Texture Domain UI · Comparison Mode · Mobile · i18n · Auth | Won't |

---

## 4. Per-file content design

### 4.1 `README.md` — public front door

**Audience**: First-time visitor on GitHub. Mix of food scientists and developers.
**Length target**: ~200 lines.

Sections:
1. **Hero** — H1 title, 1-line tagline, hero screenshot/GIF placeholder.
2. **What it is** — one paragraph.
3. **Why** — the plant-based-meat formulation problem, in plain language.
4. **Live demo** — link to the deployed Netlify URL.
5. **Tech stack** — one-line list (Svelte 5 · Plotly.js · Python/uv · Netlify).
6. **Quick start** — clone, `uv sync`, `cd frontend && npm install`, `npm run dev`.
7. **Project structure** — small annotated tree (just the top level).
8. **Documentation** — links to CLAUDE.md, PRODUCT_REQUIREMENTS, SYSTEM_ARCHITECTURE, WORKFLOWS, BUSINESS_RULES.
9. **License** — MIT.
10. **Credits** — FlavorDB2, TGSC, PubChem, Literature corpus authors, consensus.app.

### 4.2 `CLAUDE.md` — AI entry point (refresh)

**Audience**: Future Claude Code sessions.
**Length target**: ~250 lines.
**Pattern**: Mirror `lab-data-repo/CLAUDE.md` exactly.

Sections:
1. **What This Project Is** — one paragraph describing the project.
2. **Before Starting Work** — numbered checklist (read memory, read relevant docs, check files exist, never create .md files proactively, read PRD MoSCoW for current status).
3. **Tech Stack** — Python 3.12+, uv, Pydantic 2, Svelte 5, Vite, Plotly.js, jsPDF, html2canvas, Netlify.
4. **Architecture Docs** — lookup table mapping task → which doc to read first.
5. **Project Structure** — annotated tree (Python side + frontend side).
6. **Coding Style** — Python (ruff line-length, type hints, Pydantic patterns); Svelte/JS (Prettier, ESLint, Svelte 5 runes).
7. **Naming Conventions** — kebab-case slugs, `schema_version`, capability codes.
8. **Commit Conventions** — capability codes (`feat: wheel renders sunburst (#1-WV)`); searchable audit trail.
9. **Commands** — `uv sync`, `uv run python scripts/build_bundle.py`, `npm run dev`, `npm run build`, `npm run test`, `npm run e2e`.
10. **Data Flow & Ownership** — `data/source/` is truth; `bundle.json` is derived; wheel state lives in localStorage.
11. **How to Extend** — checklist for: new ingredient, new scent, new compound, new category, new sensory anchor.
12. **Constraints** — Security (XSS plain-text rule), Architecture (no live scraping, build-time only), UI (Plotly.js script loaded once).
13. **Load-Bearing Decisions** — `schema_version` enforcement, soft-delete semantics, kebab-case slugs, build-time bundle generation.

### 4.3 `docs/PRODUCT_REQUIREMENTS.md` — heartbeat

**Audience**: Maintainer (Rebecca) + AI sessions assessing what to build next.
**Length target**: ~500 lines.
**Pattern**: Mirror `lab-data-repo/PRODUCT_REQUIREMENTS.md` exactly.

Sections:
1. **Header** — Owner, Version, Last updated, Success metric, Current coverage. At spec time the counters read `0/5 bases populated, 0/5 targets populated, 0/17 capabilities done`; the PRD's status-from-code-evidence rule (§5.3 of this spec) means these numbers tick up as work lands.
2. **Problem** — what the formulation challenge is.
3. **Vision** — what the tool does for a user.
4. **MoSCoW Status** — single table, the heartbeat (17 rows from §3.4 above).
5. **Status Definitions & Maintenance Rules** — collapsible. Defines `Not started / In progress / Bug / Done` evidence requirements; capability-level rollup rules.
6. **What's Already Built** — table; currently empty (only this doc + Literature/).
7. **Capability sections** (1–16, plus Won't-have) — each:
   - Goal (1–2 sentences)
   - User story (As a … I want … so that …)
   - Feature table (Feature · Priority · Status · Notes)
   - Known issues
   - Dependencies
   - Optional `<details>` block with chart specs / interaction details
8. **Plotly Chart Conventions** — library version, interactivity, export formats, container class, fixed dimensions, script-loading rules.
9. **Architecture Constraints** — load-bearing decisions referenced from CLAUDE.md.
10. **Data Flow Reference** — small table: data type · source of truth · sync path · latency.
11. **Glossary** — scent / flavor / attribute / descriptor synonyms; on-flavor / off-flavor (internal-only); base; target; CID; etc.

### 4.4 `docs/SYSTEM_ARCHITECTURE.md`

**Audience**: Anyone designing changes to the architecture.
**Length target**: ~400 lines.
**Pattern**: Lab-data-repo SYSTEM_ARCHITECTURE.md, simplified for single-context.

Sections:
1. **Header** — Version, Date, Status, Scope.
2. **Sources synthesized** — the previous /init plan, the brainstorming spec, the example markdown corpus.
3. **TOC**.
4. **System Overview** — single bounded context; tech stack matrix; codebase summary placeholder ("0 LOC, pre-implementation").
5. **Domain Model** — Scent / Ingredient / Compound / Citation / Category / Wheel State entities.
6. **Source Architecture** — placeholder pointing to `SRC_ARCHITECTURE.md` (to be created after first scaffolding).
7. **Data Model** — JSON-shape diagrams + ERD-style relationship diagram.
8. **Workflows pointer** — link to WORKFLOWS.md.
9. **Business Rules pointer** — link to BUSINESS_RULES.md.
10. **Data Architecture** — build-time pipeline diagram (`data/source/` → Pydantic → `bundle.json` → Vite bundle → Netlify dist).
11. **Boundary Contracts** — Python/JS seam (the bundle.json contract); Netlify build contract; browser localStorage contract.
12. **Architectural Risks** — bundle size, localStorage cap, Plotly.js sunburst label-density limits, content-curation throughput.
13. **Technical Debt & Known Gaps** — currently empty (pre-implementation).

### 4.5 `docs/WORKFLOWS.md`

**Audience**: Anyone running or modifying any pipeline.
**Length target**: ~300 lines.
**Pattern**: Lab-data-repo WORKFLOWS.md, with state-machine diagrams.

Sections:
1. **Header**.
2. **Scent Lifecycle State Machine** — `created → active → deprecated`. Soft-delete semantics. Triggers and side effects.
3. **Wheel-State Lifecycle** — `in-memory → localStorage (auto-save on every change) → JSON export (manual)`. Re-import path.
4. **Build Pipeline** — `data/source/*.json` → Pydantic validation → `frontend/static/bundle.json` → Vite build → `frontend/dist/`. Run on every Netlify deploy.
5. **Deploy Pipeline** — `git push main` → Netlify build hook → `uv sync && uv run python scripts/build_bundle.py && cd frontend && npm install && npm run build` → publish `frontend/dist/`. Latency.
6. **Curation Workflow** — `Literature/` papers → consensus.app synthesis → hand-edit `data/source/*.json` → `uv run python scripts/build_bundle.py` → `npm run dev` to verify → commit + push.
7. **PubChem Fetcher Workflow** — `uv run python scripts/fetch_compound.py <CID>` → call to PubChem PUG REST `compound/cid/<CID>/property/...` endpoint → produces a Compound record draft → maintainer pastes into `data/source/compounds.json`. (Exact URL pattern documented inside the script and CLAUDE.md, not pinned in this spec.)
8. **Retry & Error Handling** — build failures (Pydantic validation; surfaced in Netlify logs); deploy failures (rollback procedure); fetcher failures (retry once, fail fast).
9. **Testing Workflow** — Pydantic schema tests at build time; Vitest unit tests for frontend logic; Playwright E2E tests against `npm run dev`.

### 4.6 `docs/BUSINESS_RULES.md`

**Audience**: Anyone adding validation, debugging a constraint, or extending the schema.
**Length target**: ~400 lines.
**Pattern**: Lab-data-repo BUSINESS_RULES.md, with 4-layer enforcement legend.

Layers (3 total — kept tight):
- **PYD** — Pydantic v2 validator (build time). Pydantic IS the schema validator; the bundle is its output.
- **JS** — Frontend guard (Svelte component / store action; runtime imports of wheel-state JSON).
- **UI** — Template-level rendering rule (e.g., plain-text-only for user content).

Sections (one per entity):
1. **Scent** — id format (kebab-case slug regex); name required; category_ids referential integrity; compounds referential integrity; sensory_anchors shape; literature referential integrity.
2. **Ingredient** — id format; scents referential integrity; deprecated propagation rules.
3. **Compound** — id format; cid optional but unique-when-present; synonyms array; cas_number format optional.
4. **Citation** — id format; doi or url required (at least one); source_kind enum; local_pdf_filename references actual file in Literature/.
5. **Category** — id format; parent_id existence-or-null; default_color hex format.
6. **Wheel State** — schema_version exact match (1); app_version present; ingredients role enum; scent IDs resolvable; localStorage size cap (~1 MB).
7. **Cross-cutting** — kebab-case slug regex (`^[a-z0-9]+(-[a-z0-9]+)*$`); schema_version `1`; hex color format; soft-delete semantics; plain-text rendering rule for user content.

---

## 5. Cross-document consistency rules

These hold across the 6 files. Violations are spec bugs.

1. **Schema fields are defined ONCE.** The authoritative shape lives in BUSINESS_RULES.md. SYSTEM_ARCHITECTURE.md and CLAUDE.md reference it; PRD references it for capability-specific feature notes. No file redefines a field's shape.
2. **Capability codes are the join key.** PRD section IDs (`#1-WV`, `#2-IP`, …) appear in commit messages (CLAUDE.md "Commit Conventions") and may appear in WORKFLOWS.md when describing how a capability is built.
3. **Status in PRD is derived from code evidence**, not authored from memory. While code doesn't exist, every status is `Not started`. Once code lands, the PRD's Status Definitions section drives how rows are updated.
4. **Cross-references use markdown links**, not "see the other doc" prose. Concrete navigation.
5. **No file exceeds its length target by >50%.** If a section grows beyond budget, it gets split out (e.g., DATA_MODEL.md split from SYSTEM_ARCHITECTURE.md).

---

## 6. Out of scope for this design spec

- **Specific category-color hex values.** Will be picked during the frontend-design phase, after we see the wheel render.
- **Visual aesthetic** (modern minimal vs. scientific vs. editorial). Will be picked during frontend-design.
- **Specific commit conventions** beyond capability codes. Default to conventional-commits-style otherwise.
- **CI configuration** (GitHub Actions). Defer to implementation phase.
- **Test-suite specifics.** Defer to implementation phase.

---

## 7. Risks

1. **Doc rot.** All 6 files are written before any code. As code lands, the docs need to track. Mitigated by: (a) PRD's "derive from code evidence" rule; (b) `claude-md-management:revise-claude-md` skill for refreshing CLAUDE.md; (c) the explicit "Pointer for future sessions" section noting docs should be regenerated after first scaffolding.
2. **Scope creep within the docs.** A doc-suite phase can balloon into infinite-detail-prose. Length targets above bound the work. Cross-references mean each fact lives in exactly one file.
3. **Premature commitment.** Some decisions (color palette, exact PDF page layout) are deliberately deferred to the frontend-design phase. The docs flag these as TBD rather than guessing.
4. **Internal inconsistency.** Six files sharing schemas is a consistency surface. Mitigated by the spec-document-reviewer subagent post-write.

---

## 8. Definition of done for this phase

- All 6 markdown files exist at the paths in §2.
- All §5 cross-document consistency rules pass.
- The spec-document-reviewer subagent approves each file.
- The maintainer (Rebecca) has reviewed and signed off.

After done: invoke `superpowers:writing-plans` to plan the actual implementation (scaffolding + curation + frontend build).

---

## 9. Approval

This spec is for human review. After Rebecca approves:
1. Spec is committed to git (after `git init`).
2. `superpowers:writing-plans` is invoked to plan how to actually write the 6 files.
3. The 6 files are produced per the plan.
4. Spec-review subagent runs on each file.
5. Cleanup, commit, done.
