<script>
  import { onMount } from 'svelte';
  import { loadBundle } from './lib/data.js';
  import Wheel from './components/Wheel.svelte';
  import Sidebar from './components/Sidebar.svelte';
  import SidePanel from './components/SidePanel.svelte';

  let loaded = $state(false);
  let error = $state(null);

  onMount(async () => {
    try {
      await loadBundle();
      loaded = true;
    } catch (err) {
      error = err.message || String(err);
    }
  });
</script>

<header>
  <h1>Sensory Wheel</h1>
</header>

{#if error}
  <main style="grid-area: wheel;"><p style="color: #b00;">Failed to load bundle: {error}</p></main>
{:else if !loaded}
  <main style="grid-area: wheel;"><p>Loading…</p></main>
{:else}
  <Sidebar />
  <div class="wheel-area">
    <Wheel />
  </div>
  <SidePanel />
{/if}
