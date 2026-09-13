<script lang="ts">
  import { onMount } from 'svelte';
  import { authenticate, play, endRound, getReplay, readEngineParams, formatEngineAmount } from './lib/rgs';

  const symbols = ['watch','diamond','ace','gold','cash','passport','bag','bust','wild','vip'];
  const params = readEngineParams();
  let board = Array.from({length: 20}, (_, i) => symbols[i % symbols.length]);
  let balance = 0;
  let currency = params.currency;
  let betLevels: number[] = [];
  let bet = 0;
  let win = 0;
  let loading = true;
  let spinning = false;
  let error = '';
  let rulesOpen = false;
  let muted = true;
  let turbo = false;
  let replayReady = false;
  let replayData: any = null;
  let jurisdiction: any = {};

  const demoMode = !params.rgsUrl || (!params.sessionID && !params.replay);

  function normalizeBoard(events: any[]) {
    const reveal = events.find((e:any) => e?.type === 'reveal' && e?.board);
    if (!reveal) return null;
    const raw = Array.isArray(reveal.board?.[0]) ? reveal.board.flat() : reveal.board;
    return raw.slice(0,20).map((s:any) => typeof s === 'string' ? s.toLowerCase() : String(s?.name || s?.symbol || 'cash').toLowerCase());
  }

  function randomBoard() {
    board = Array.from({length:20}, () => symbols[Math.floor(Math.random()*symbols.length)]);
  }

  async function initialise() {
    try {
      if (params.replay) {
        replayData = await getReplay(params.rgsUrl, params.game, params.version, params.mode, params.event);
        currency = params.currency;
        bet = params.amount;
        replayReady = true;
      } else if (demoMode) {
        balance = 991.30 * 1_000_000;
        currency = 'USD';
        betLevels = [10000,20000,50000,100000,200000,500000,1000000,2000000,5000000];
        bet = 1000000;
      } else {
        const auth = await authenticate(params.rgsUrl, params.sessionID);
        balance = auth.balance.amount;
        currency = auth.balance.currency;
        betLevels = auth.config.betLevels?.length ? auth.config.betLevels : [auth.config.minBet, auth.config.defaultBetLevel, auth.config.maxBet];
        bet = auth.config.defaultBetLevel;
        jurisdiction = auth.config.jurisdiction || {};
        if (auth.round && (auth.round as any).active) await applyRound(auth.round);
      }
    } catch (e:any) {
      error = e?.data?.code || e?.message || 'Unable to start game';
    } finally { loading = false; }
  }

  async function applyRound(round:any) {
    const events = round?.events || round?.state?.events || [];
    const next = normalizeBoard(events);
    if (next?.length === 20) board = next;
    const payout = Number(round?.payoutMultiplier ?? round?.state?.payoutMultiplier ?? 0);
    win = Math.round(bet * payout / 100);
    await new Promise(r => setTimeout(r, turbo ? 180 : 650));
  }

  async function spin() {
    if (spinning || params.replay) return;
    error = '';
    spinning = true;
    win = 0;
    try {
      if (demoMode) {
        if (balance < bet) throw new Error('Insufficient balance');
        balance -= bet;
        await new Promise(r=>setTimeout(r,turbo?180:650));
        randomBoard();
        if (Math.random() < .28) { win = bet * (Math.random() < .08 ? 10 : 2); balance += win; }
      } else {
        const result = await play(params.rgsUrl, params.sessionID, bet, 'base');
        if (result.balance) balance = result.balance.amount;
        if (result.round) await applyRound(result.round);
        try {
          const ended = await endRound(params.rgsUrl, params.sessionID);
          if (ended.balance) balance = ended.balance.amount;
        } catch { /* some math configs auto-close */ }
      }
    } catch (e:any) { error = e?.data?.code || e?.message || 'Bet failed'; }
    finally { spinning = false; }
  }

  async function playReplay() {
    if (!replayData) return;
    spinning = true;
    const state = replayData.state || replayData.round || replayData;
    const events = state.events || [];
    const next = normalizeBoard(events);
    if (next?.length === 20) board = next;
    const payout = Number(replayData.payoutMultiplier ?? state.payoutMultiplier ?? 0);
    win = Math.round((bet || 0) * payout);
    await new Promise(r=>setTimeout(r,700));
    spinning = false;
  }

  function moveBet(delta:number) {
    const idx = Math.max(0, betLevels.findIndex(v => v === bet));
    bet = betLevels[Math.max(0, Math.min(betLevels.length-1, idx + delta))] ?? bet;
  }

  onMount(initialise);
</script>

<div class="game" class:replay={params.replay}>
  <div class="veil"></div>
  <header><img src="./logo.webp" alt="Black Market"><span>RARE ITEMS · BIGGER STORIES</span></header>
  <main>
    <div class="reels" class:spinning>
      {#each board as symbol}
        <div class="cell"><img src={`./symbols/${symbols.includes(symbol) ? symbol : 'cash'}.svg`} alt={symbol}></div>
      {/each}
    </div>
  </main>
  <aside class="lot"><img src="./artifact.webp" alt="Lot 001"><small>LOT 001 · THE UNKNOWN</small></aside>

  {#if loading}<div class="overlay">CONNECTING…</div>{/if}
  {#if error}<div class="error">{error}</div>{/if}

  <footer>
    <button class="icon" on:click={() => rulesOpen = true}>i</button>
    {#if !params.replay}
      <div><small>BALANCE</small><b>{formatEngineAmount(balance,currency)}</b></div>
      <button class="step" on:click={() => moveBet(-1)} disabled={spinning}>−</button>
      <div><small>BET</small><b>{formatEngineAmount(bet,currency,true)}</b></div>
      <button class="step" on:click={() => moveBet(1)} disabled={spinning}>+</button>
    {/if}
    <div><small>WIN</small><b>{formatEngineAmount(win,currency,true)}</b></div>
    {#if params.replay}
      <button class="replay-btn" on:click={playReplay} disabled={!replayReady || spinning}>{spinning ? 'PLAYING' : 'PLAY REPLAY'}</button>
    {:else}
      <button class="spin" on:click={spin} disabled={spinning}>↻</button>
      <button on:click={() => muted = !muted}>{muted ? 'SOUND OFF' : 'SOUND ON'}</button>
      {#if !jurisdiction?.disabledTurbo}<button class:active={turbo} on:click={() => turbo = !turbo}>TURBO</button>{/if}
    {/if}
  </footer>

  {#if rulesOpen}
    <section class="modal">
      <div>
        <button class="close" on:click={() => rulesOpen=false}>×</button>
        <h2>BLACK MARKET</h2>
        <p>5×4 premium slot. Winning outcomes are determined exclusively by Stake Engine RGS math files. The frontend never generates production outcomes.</p>
        <h3>GAME INFORMATION</h3>
        <p>Target RTP: 96.00% · Maximum win target: 5,000×. These values must match the approved published math package before release.</p>
        <h3>CONTROLS</h3><p>Spin: place bet · +/−: select only bet levels supplied by RGS · Turbo: faster presentation when jurisdiction permits · Spacebar: spin.</p>
        <h3>PAYTABLE</h3><p>Final symbol payouts and special-symbol values are supplied by the approved math model and must be mirrored here before submission.</p>
      </div>
    </section>
  {/if}
</div>

<svelte:window on:keydown={(e) => { if (e.code === 'Space' && !params.replay && !rulesOpen) { e.preventDefault(); spin(); } }} />
