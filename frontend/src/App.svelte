<script>
  import { onMount } from 'svelte';
  import { loadBundle } from './lib/data.js';
  import Wheel from './components/Wheel.svelte';

  let loaded = false;
  let error = null;

  onMount(async () => {
    try {
      await loadBundle();
      loaded = true;
    } catch (err) {
      error = err.message;
    }
  });
</script>

<main>
  <h1>Sensory Wheel</h1>
  {#if error}
    <p class="error">Failed to load bundle: {error}</p>
  {:else if !loaded}
    <p>Loading…</p>
  {:else}
    <div class="wheel-area">
      <Wheel />
    </div>
  {/if}
</main>

<style>
  main { padding: 2rem; font-family: system-ui, sans-serif; }
  .error { color: #b00; }
  .wheel-area { width: 600px; height: 600px; margin: 0 auto; }
</style>
