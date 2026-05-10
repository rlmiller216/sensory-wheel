<script>
  import { wheelState } from '../lib/store.js';
  import { getBundle } from '../lib/data.js';

  const ingredients = getBundle().ingredients;

  // Read role assignments from the store.
  const baseId = $derived(
    $wheelState.ingredients.find((i) => i.role === 'base')?.ingredient_id ?? ''
  );
  const targetId = $derived(
    $wheelState.ingredients.find((i) => i.role === 'target')?.ingredient_id ?? ''
  );

  function setRole(role, newId) {
    wheelState.update((state) => {
      const others = state.ingredients.filter((i) => i.role !== role);
      return {
        ...state,
        ingredients: [...others, { ingredient_id: newId, role }],
        scents_displayed: [],   // clear so the union recomputes
      };
    });
  }
</script>

<aside class="sidebar">
  <h2>Ingredients</h2>

  <label>
    Base
    <select value={baseId} onchange={(e) => setRole('base', e.currentTarget.value)}>
      {#each ingredients as ing}
        <option value={ing.id}>{ing.name}</option>
      {/each}
    </select>
  </label>

  <label>
    Target
    <select value={targetId} onchange={(e) => setRole('target', e.currentTarget.value)}>
      {#each ingredients as ing}
        <option value={ing.id}>{ing.name}</option>
      {/each}
    </select>
  </label>
</aside>

<style>
  .sidebar { padding: 1rem; border-right: 1px solid #ddd; }
  .sidebar label { display: block; margin: 0.5rem 0; font-size: 0.9rem; }
  .sidebar select { display: block; margin-top: 0.25rem; width: 100%; padding: 0.25rem; }
</style>
