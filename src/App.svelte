<script lang="ts">
  import { onMount } from 'svelte';
  import './game/game.css';
  import ReelsCanvas from './game/components/ReelsCanvas.svelte';
  import { DEMO_ROUNDS } from './game/engine/demoRounds';
  import type { EventPlayer } from './game/engine/EventPlayer';
  import { parseRoundBook } from './game/engine/roundBook';
  import { initialGameState, type GameState } from './game/state/gameState';
  import type { GameEvent, RoundBook } from './game/events/types';
  import { authenticate, play, endRound, getReplay, readEngineParams, formatEngineAmount } from './lib/rgs';

  const params = readEngineParams();
  const demoMode = !params.rgsUrl || (!params.sessionID && !params.replay);
  const backgroundUrl = new URL('./background.webp', document.baseURI).href;
  let player = $state<EventPlayer | null>(null);
  let pendingBook = $state<RoundBook | null>(null);
  let replayBook = $state<RoundBook | null>(null);
  let gameState = $state<GameState>(initialGameState());
  let balance = $state(0);
  let currency = $state(params.currency);
  let betLevels = $state<number[]>([]);
  let bet = $state(0);
  let win = $state(0);
  let loading = $state(true);
  let spinning = $state(false);
  let error = $state('');
  let rulesOpen = $state(false);
  let muted = $state(true);
  let turbo = $state(false);
  let replayReady = $state(false);
  let jurisdiction = $state<Record<string, unknown>>({});

  function roundFrom(value: unknown) {
    const record = value as Record<string, unknown>;
    return parseRoundBook(record?.state ?? record?.round ?? record);
  }

  async function playBook(book: RoundBook) {
    if (!player) { pendingBook = book; return; }
    spinning = true;
    try {
      const state = await player.play(book.events);
      win = Math.round(bet * state.totalWin);
    } finally { spinning = false; }
  }

  async function onRendererReady(next: EventPlayer) {
    player = next;
    if (pendingBook) { const book = pendingBook; pendingBook = null; await playBook(book); }
    else if (demoMode) await next.play([DEMO_ROUNDS[0].events[0]]);
  }

  function onGameState(state: GameState, _event: GameEvent) {
    gameState = state;
    win = Math.round(bet * state.totalWin);
  }

  async function initialise() {
    try {
      if (params.replay) {
        replayBook = roundFrom(await getReplay(params.rgsUrl, params.game, params.version, params.mode, params.event));
        currency = params.currency;
        bet = params.amount;
        replayReady = true;
      } else if (demoMode) {
        balance = 991_300_000;
        currency = 'USD';
        betLevels = [100_000, 200_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000];
        bet = 1_000_000;
      } else {
        const auth = await authenticate(params.rgsUrl, params.sessionID);
        balance = auth.balance.amount;
        currency = auth.balance.currency;
        betLevels = auth.config.betLevels?.length ? auth.config.betLevels : [auth.config.minBet, auth.config.defaultBetLevel, auth.config.maxBet];
        bet = auth.config.defaultBetLevel;
        jurisdiction = auth.config.jurisdiction || {};
        if (auth.round && (auth.round as Record<string, unknown>).active) {
          const activeBook = roundFrom(auth.round);
          if (player) await playBook(activeBook); else pendingBook = activeBook;
        }
      }
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Unable to start game';
    } finally { loading = false; }
  }

  async function spin() {
    if (spinning || params.replay || !player) return;
    error = '';
    win = 0;
    try {
      if (demoMode) {
        if (balance < bet) throw new Error('Insufficient balance');
        balance -= bet;
        const book = DEMO_ROUNDS[0];
        await playBook(book);
        balance += Math.round(bet * book.payoutMultiplier);
      } else {
        spinning = true;
        const result = await play(params.rgsUrl, params.sessionID, bet, 'base');
        if (result.balance) balance = result.balance.amount;
        if (!result.round) throw new Error('RGS response is missing round data');
        await playBook(roundFrom(result.round));
        const ended = await endRound(params.rgsUrl, params.sessionID);
        if (ended.balance) balance = ended.balance.amount;
      }
    } catch (cause) {
      error = cause instanceof Error ? cause.message : 'Bet failed';
    } finally { spinning = false; }
  }

  async function playReplay() {
    if (!replayBook || spinning) return;
    await playBook(replayBook);
  }

  function moveBet(delta: number) {
    if (spinning) return;
    const index = Math.max(0, betLevels.findIndex((value) => value === bet));
    bet = betLevels[Math.max(0, Math.min(betLevels.length - 1, index + delta))] ?? bet;
  }

  onMount(initialise);
</script>

<div class="game" class:replay={params.replay} style:background-image={`linear-gradient(90deg,rgba(33,30,27,.68),rgba(240,224,199,.10),rgba(42,38,34,.58)),url("${backgroundUrl}")`}>
  <div class="veil"></div>
  <header><img src="./logo.webp" alt="Black Market"><span>RARE ITEMS · BIGGER STORIES</span></header>
  <main><ReelsCanvas onReady={onRendererReady} onState={onGameState} onError={(message) => error = message} {turbo} /></main>
  <aside class="lot"><img src="./artifact.webp" alt="Lot 001"><small>LOT 001 · THE UNKNOWN</small></aside>

  <section class="feature-status" aria-live="polite">
    {#if gameState.holdSpin.active}
      <b>HOLD & SPIN</b><span>{gameState.holdSpin.respins} RESPINS · {Object.keys(gameState.holdSpin.locked).length} LOCKED</span>
    {:else if gameState.freeSpins.active}
      <b>FREE SPINS {gameState.freeSpins.current}/{gameState.freeSpins.total}</b><span>{gameState.freeSpins.multiplier}× MULTIPLIER</span>
    {:else if gameState.cascade > 0 && spinning}
      <b>CASCADE {gameState.cascade}</b>
    {/if}
  </section>

  {#if loading}<div class="overlay">CONNECTING…</div>{/if}
  {#if error}<div class="error" role="alert">{error}</div>{/if}

  <footer>
    <button class="icon" onclick={() => rulesOpen = true} aria-label="Open game information">i</button>
    {#if !params.replay}
      <div><small>BALANCE</small><b>{formatEngineAmount(balance, currency)}</b></div>
      <button class="step" onclick={() => moveBet(-1)} disabled={spinning} aria-label="Decrease bet">−</button>
      <div><small>BET</small><b>{formatEngineAmount(bet, currency, true)}</b></div>
      <button class="step" onclick={() => moveBet(1)} disabled={spinning} aria-label="Increase bet">+</button>
    {/if}
    <div><small>WIN</small><b>{formatEngineAmount(win, currency, true)}</b></div>
    {#if params.replay}
      <button class="replay-btn" onclick={playReplay} disabled={!replayReady || spinning}>{spinning ? 'PLAYING' : 'PLAY REPLAY'}</button>
    {:else}
      <button class="spin" onclick={spin} disabled={spinning || !player} aria-label="Spin">↻</button>
      <button onclick={() => muted = !muted}>{muted ? 'SOUND OFF' : 'SOUND ON'}</button>
      {#if !jurisdiction.disabledTurbo}<button class:active={turbo} onclick={() => turbo = !turbo}>TURBO</button>{/if}
    {/if}
  </footer>

  {#if rulesOpen}
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="rules-title">
      <div>
        <button class="close" onclick={() => rulesOpen = false} aria-label="Close game information">×</button>
        <h2 id="rules-title">BLACK MARKET</h2>
        <p>5×4 cascading reels with expanding Wilds, Free Spins, a progressive Free Spins multiplier, and Hold & Spin. Production results are played exclusively from ordered Stake Engine events.</p>
        <h3>GAME INFORMATION</h3>
        <p>Target RTP is provisionally configured at 96.00%. It is not certified. Final RTP, maximum win, volatility, paytable, and feature frequencies require simulation and approval.</p>
        <h3>CONTROLS</h3><p>Spin places a bet. Bet controls use only levels supplied by the RGS. Turbo changes presentation speed when the jurisdiction permits it. Spacebar activates Spin.</p>
      </div>
    </div>
  {/if}
</div>

<svelte:window onkeydown={(event) => { if (event.code === 'Space' && !params.replay && !rulesOpen && event.target === document.body) { event.preventDefault(); spin(); } }} />
