// Build a Plotly.js sunburst figure from the bundle + wheel state.
//
// v0: minimal — equal-area wedges, category colors only, no per-scent overrides.
// Polish (color overrides, depth control, labels) lands in later capabilities.

import { findScent, findCategory } from './data.js';

export function buildSunburstFigure(scentIds) {
  // Plotly sunburst expects parallel arrays: ids, labels, parents.
  // ids: unique node IDs.
  // parents: ID of the parent node (empty string for root).
  // labels: display text per node.

  const ids = [];
  const labels = [];
  const parents = [];
  const colors = [];

  // Track which categories we've already added (each may be referenced by
  // multiple scents — Plotly nodes must be unique).
  const seenCategories = new Set();

  for (const scentId of scentIds) {
    const scent = findScent(scentId);
    if (!scent) continue;
    // A scent in multiple categories renders once per category (synthetic
    // per-category node ID = `<category>:<scent>`).
    for (const catId of scent.category_ids) {
      const cat = findCategory(catId);
      if (!cat) continue;
      if (!seenCategories.has(catId)) {
        ids.push(catId);
        labels.push(cat.name);
        parents.push('');
        colors.push(cat.default_color ?? '#cccccc');
        seenCategories.add(catId);
      }
      const nodeId = `${catId}:${scentId}`;
      ids.push(nodeId);
      labels.push(scent.name);
      parents.push(catId);
      colors.push(cat.default_color ?? '#cccccc');
    }
  }

  return {
    data: [
      {
        // v0: equal-area wedges (no `values` array supplied → Plotly sizes leaves
        // by count, parents by sum of leaves). Using `branchvalues: 'remainder'`
        // (Plotly's default) so that when per-scent intensity `values` are added
        // in a future capability, the behavior degrades gracefully — parent
        // wedges stay independent rather than auto-summing.
        type: 'sunburst',
        ids,
        labels,
        parents,
        marker: { colors },
        branchvalues: 'remainder',
        leaf: { opacity: 0.85 },
      },
    ],
    layout: {
      margin: { l: 0, r: 0, t: 0, b: 0 },
      paper_bgcolor: 'transparent',
      font: { family: 'system-ui, sans-serif', size: 12 },
    },
    config: { responsive: true, displayModeBar: false },
  };
}
