<script lang="ts">
  import { onMount } from 'svelte';
  import { GameRenderer } from '../pixi/GameRenderer';
  import type { GameEvent } from '../events/types';
  import type { GameState } from '../state/gameState';
  import { EventPlayer } from '../engine/EventPlayer';

  let { onReady, onState, onError, turbo = false }: {
    onReady: (player: EventPlayer) => void;
    onState: (state: GameState, event: GameEvent) => void;
    onError: (message: string) => void;
    turbo?: boolean;
  } = $props();
  let host: HTMLDivElement;

  onMount(() => {
    const renderer = new GameRenderer();
    let disposed = false;
    renderer.mount(host).then(() => {
      if (!disposed) onReady(new EventPlayer(renderer, onState, () => turbo ? 70 : 230));
    }).catch((cause) => onError(cause instanceof Error ? cause.message : 'Unable to initialize game renderer'));
    return () => { disposed = true; renderer.destroy(); };
  });
</script>

<div class="reels-canvas" bind:this={host} aria-label="Five reel by four row BLACK MARKET game board"></div>
