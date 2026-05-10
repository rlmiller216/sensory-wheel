// Wheel state — the single source of truth for what the user has configured.
// Shape mirrors BUSINESS_RULES.md §6 (Wheel State).
//
// On every change, syncs to localStorage so a refresh doesn't lose work.
// On boot, attempts to load from localStorage (falls back to defaults if absent
// or schema_version mismatch).

import { writable } from 'svelte/store';

const STORAGE_KEY = 'sensory_wheel_state';
const SCHEMA_VERSION = 1;

// Default state — soy + beef demo. See PRD §1 (WV) for rationale.
const DEFAULT_STATE = {
  schema_version: SCHEMA_VERSION,
  app_version: '0.1.0',
  name: 'Demo wheel',
  description: '',
  author: null,
  created_at: null,
  updated_at: null,
  ingredients: [
    { ingredient_id: 'soy', role: 'base' },
    { ingredient_id: 'beef', role: 'target' },
  ],
  scents_displayed: [],     // empty = compute from ingredients (union)
  custom_scents: [],
  color_overrides: {},
  hierarchy_depth: 3,
  definitions_visible: false,
  annotations: {},
};

function loadInitialState() {
  const now = new Date().toISOString();
  const fresh = () => ({
    ...DEFAULT_STATE,
    ingredients: DEFAULT_STATE.ingredients.map((i) => ({ ...i })),
    custom_scents: [],
    color_overrides: {},
    annotations: {},
    created_at: now,
    updated_at: now,
  });

  if (typeof localStorage === 'undefined') return fresh();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return fresh();
    const parsed = JSON.parse(raw);
    // LocalStorage is opaque to the user — they can't see or edit the value,
    // so a silent reset is the right UX for a schema bump. File imports
    // (capability #7-IO, deferred) WILL throw on a version mismatch; if this
    // logic is ever reused for file imports, split it.
    if (parsed.schema_version !== SCHEMA_VERSION) {
      console.warn('schema_version mismatch in saved wheel state; resetting to defaults');
      return fresh();
    }
    return parsed;
  } catch (err) {
    console.warn('failed to load saved wheel state; resetting to defaults', err);
    return fresh();
  }
}

export const wheelState = writable(loadInitialState());

// Auto-save on every change.
if (typeof localStorage !== 'undefined') {
  wheelState.subscribe((state) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (err) {
      console.warn('failed to save wheel state to localStorage', err);
    }
  });
}
