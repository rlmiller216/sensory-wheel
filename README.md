# Sensory Wheel

*Interactive sunburst chart for plant-based-meat flavor formulation.*

<!-- TODO: capture hero screenshot/GIF after first deploy -->
<p align="center">
  <img src="docs/images/hero.png" alt="Sensory Wheel demo" width="700" />
</p>

---

## What it is

Sensory Wheel is a static interactive web app that maps the aroma landscape of
plant-based-meat formulation. Pick a **base** ingredient — pea protein, soy,
mycelium, wheat gluten, or faba bean — and a **target** meat profile — beef,
chicken, pork, fish, or lamb — and the app renders a multi-layer sunburst chart
showing the union of all associated scents organized by aromatic family (Floral,
Fruity, Vegetal, Roasted, Spicy, Animal, Mineral, Off-notes). Click any wedge
to open a side panel with the scent's definition, sensory anchors, constituent
aroma compounds, and literature citations. Export the finished wheel as SVG,
PNG, PDF, or JSON for documentation and sharing.

The first load drops you into a pre-populated demo: **soy (base) × beef
(target)**. No login, no server — the full dataset ships as a single
`bundle.json` built from curated research at deploy time.

---

## Why

Plant-based-meat formulation is a masking and mimicry problem. Plant proteins
carry inherent off-notes — beany, grassy, chalky, oxidized — that need to be
suppressed, while the defining flavor signatures of the target meat must be
built up through deliberate ingredient and flavor choices. A formulator working
on a pea-protein burger needs to know two things at once: which notes are
already present in the base, and which notes define the beef target.

Where those two sets overlap are the **bridge flavors** — scents that are
already naturally aligned between where you are and where you want to be.
Identifying bridge flavors early focuses development effort and reduces the risk
of overworking a formulation. Today, formulators piece this together from paper
references and mental models, making it slow to research and hard to share
across sessions. Sensory Wheel puts the full aroma landscape on a single
interactive surface, making bridge flavors immediately visible and drillable
down to the compound and citation level.

---

## Live demo

[sensory-wheel.netlify.app →](https://sensory-wheel.netlify.app/)

<!-- TODO: confirm URL at first deploy; update the link above -->

---

## Tech stack

- **Frontend:** Svelte 5 (Vite) + Plotly.js (`plotly.js-strict-dist-min` slim build, ~800 KB)
- **In-browser PDF:** jsPDF + html2canvas (Plotly canvas capture)
- **Build-time curation:** Python 3.12+ with `uv`, Pydantic v2 for schema validation
- **Hosting:** Netlify (static — no server, no cold starts)

All curation runs at **build time** — the deployed app makes no live network
calls after loading. Pydantic validates every curated JSON record before the
bundle is written; a validation error aborts the build rather than shipping
broken data.

---

## Quick start

```bash
git clone https://github.com/<your-username>/sensory-wheel
cd sensory-wheel

# Install Python deps and curate the bundle
uv sync
uv run python scripts/build_bundle.py

# Run the frontend dev server
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173/` to see the wheel.

The dev server reloads on frontend changes. To re-run curation after editing
`data/source/` JSON, re-run `uv run python scripts/build_bundle.py` from the
repo root (not from `frontend/`).

**Other useful commands:**

```bash
# Python (run from repo root)
uv run pytest tests/ -v                         # schema and unit tests
uv run python scripts/fetch_compound.py <CID>   # draft a compound record from PubChem

# Frontend (run from frontend/)
npm run build     # production build → frontend/dist/
npm run test      # Vitest unit tests
npm run e2e       # Playwright E2E tests (requires npm run dev in another terminal)
```

---

## Project structure

```
sensory_wheel/    # Python package: schemas, load, bundle (build-time only)
scripts/          # Python entrypoints (build_bundle, fetch_compound)
data/source/      # Hand-curated JSON — the source of truth
frontend/         # Svelte 5 app (the deployed thing)
tests/            # Python tests (pytest)
docs/             # Architecture, requirements, business rules, workflows
Literature/       # Maintainer's research PDFs
```

`bundle.json` is generated at build time and gitignored — `data/source/` is the
only hand-edited truth. Running `uv run python scripts/build_bundle.py` writes
`frontend/static/bundle.json`, which Vite bundles into the static dist.

---

## Documentation

- [`CLAUDE.md`](./CLAUDE.md) — project rules and conventions for AI sessions
- [`docs/PRODUCT_REQUIREMENTS.md`](./docs/PRODUCT_REQUIREMENTS.md) — what we're building (MoSCoW heartbeat)
- [`docs/SYSTEM_ARCHITECTURE.md`](./docs/SYSTEM_ARCHITECTURE.md) — overall system design
- [`docs/WORKFLOWS.md`](./docs/WORKFLOWS.md) — pipelines and state machines
- [`docs/BUSINESS_RULES.md`](./docs/BUSINESS_RULES.md) — schema authority and validation rules

---

## License

MIT — see [LICENSE](./LICENSE) for details.

---

## Credits

- Built by [Rebecca Miller](https://github.com/rlmiller216) <!-- TODO: replace with portfolio URL if available -->
- Compound data via [PubChem](https://pubchem.ncbi.nlm.nih.gov/) (NIH NLM)
- Reference material via [FlavorDB2](https://cosylab.iiitd.edu.in/flavordb2) (IIIT Delhi) and [The Good Scents Company](https://www.thegoodscentscompany.com/)
- Research synthesis via [Consensus](https://consensus.app/)
- Literature corpus: 13 papers on meat / fish / poultry flavor chemistry (see [`Literature/`](./Literature/) — full bibliography in [`data/source/citations.json`](./data/source/citations.json))
