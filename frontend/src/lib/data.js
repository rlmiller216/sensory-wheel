// Fetches bundle.json once at app boot and exposes lookup helpers.
//
// The bundle is treated as immutable. All schema validation happened
// at build time (Pydantic) — the frontend trusts the bundle.

let _bundle = null;

export async function loadBundle() {
  if (_bundle) return _bundle;
  const response = await fetch('/bundle.json');
  if (!response.ok) {
    throw new Error(`failed to load bundle.json: ${response.status} ${response.statusText}`);
  }
  _bundle = await response.json();
  return _bundle;
}

export function getBundle() {
  if (!_bundle) throw new Error('bundle not loaded yet — call loadBundle() first');
  return _bundle;
}

// Lookups (only valid after loadBundle() resolves).

export function findScent(id) {
  return getBundle().scents.find((s) => s.id === id) ?? null;
}

export function findIngredient(id) {
  return getBundle().ingredients.find((i) => i.id === id) ?? null;
}

export function findCategory(id) {
  return getBundle().taxonomy.find((c) => c.id === id) ?? null;
}

// Compute the union of scent IDs from a list of {ingredient_id, role}.
export function unionScents(ingredientList) {
  const set = new Set();
  for (const { ingredient_id } of ingredientList) {
    const ing = findIngredient(ingredient_id);
    if (!ing) continue;
    for (const sid of ing.scents) set.add(sid);
  }
  return [...set];
}
