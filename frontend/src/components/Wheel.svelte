<script>
  import Plotly from 'plotly.js-strict-dist-min';
  import { buildSunburstFigure } from '../lib/wheel.js';
  import { unionScents } from '../lib/data.js';
  import { wheelState } from '../lib/store.js';

  let containerEl;

  $effect(() => {
    // Re-runs on every $wheelState change.
    const state = $wheelState;
    if (!containerEl) return;
    const scentIds = state.scents_displayed.length > 0
      ? state.scents_displayed
      : unionScents(state.ingredients);
    const figure = buildSunburstFigure(scentIds);
    Plotly.react(containerEl, figure.data, figure.layout, figure.config);

    return () => {
      // Cleanup when the effect re-runs or the component unmounts.
      if (containerEl) Plotly.purge(containerEl);
    };
  });
</script>

<div class="wheel" bind:this={containerEl}></div>

<style>
  .wheel {
    width: 100%;
    height: 100%;
    min-height: 480px;
  }
</style>
