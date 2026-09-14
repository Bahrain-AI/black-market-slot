/**
 * Frontend parser acceptance against verbatim Engine book payloads.
 *
 * These fixtures are complete rounds extracted from the provisional SDK pipeline
 * books (math/.stake-engine/math-sdk/games/black_market/library/publish_files/books_<mode>.jsonl.zst)
 * and exercise the full 16-event frontend contract: the base cascade family, the
 * free-spins family and the hold & spin family. They are format fixtures, not
 * RTP evidence; regenerate from the approved production books before ACP staging:
 *
 *   python math/tools/find_sdk_replays.py            # records per-mode replay IDs
 *   # extract <id> books below via the same decompressor, then re-emit this file.
 */
import { describe, expect, it } from 'vitest';
import { parseRoundBook } from './roundBook';
import type { GameEvent, PayoutEvent, RoundEndEvent } from '../events/types';

const CONTRACT_TYPES = new Set<GameEvent['type']>([
  'reveal', 'win', 'cascade', 'removeSymbols', 'collapse', 'refill', 'expandingWild',
  'freeSpinsStart', 'freeSpin', 'multiplierIncrease', 'holdSpinStart', 'holdSpinLock',
  'holdSpinRespins', 'holdSpinEnd', 'payout', 'roundEnd'
]);

// Verbatim rounds from the provisional pipeline:
//   base loss (payout 0)
//   id=6 payoutMultiplier=0 events=3 types=payout,reveal,roundEnd
//   base free-spins cascade round
//   id=2868 payoutMultiplier=610 events=42 types=cascade,collapse,expandingWild,freeSpin,freeSpinsStart,multiplierIncrease,payout,refill,removeSymbols,reveal,roundEnd,win
//   vault hold & spin (respins, no new locks)
//   id=187 payoutMultiplier=6400 events=11 types=holdSpinEnd,holdSpinRespins,holdSpinStart,payout,refill,reveal,roundEnd
//   vault hold & spin with a new lock
//   id=498 payoutMultiplier=1700 events=14 types=holdSpinEnd,holdSpinLock,holdSpinRespins,holdSpinStart,payout,refill,reveal,roundEnd

const baseLossRound = JSON.parse('{"id":6,"payoutMultiplier":0,"events":[{"index":0,"type":"reveal","board":[[{"name":"H3"},{"name":"L3"},{"name":"H4"},{"name":"L4"}],[{"name":"L4"},{"name":"L1"},{"name":"S"},{"name":"L2"}],[{"name":"L3"},{"name":"H4"},{"name":"L4"},{"name":"L1"}],[{"name":"L1"},{"name":"H1"},{"name":"L2"},{"name":"H2"}],[{"name":"S"},{"name":"L4"},{"name":"H4"},{"name":"L1"}]]},{"index":1,"type":"payout","amount":0,"total":0},{"index":2,"type":"roundEnd","payoutMultiplier":0}],"criteria":"0","baseGameWins":0.0,"freeGameWins":0.0}') as unknown;

const baseFreeSpinsRound = JSON.parse('{"id":2868,"payoutMultiplier":610,"events":[{"index":0,"type":"reveal","board":[[{"name":"H2"},{"name":"L2"},{"name":"H3"},{"name":"S"}],[{"name":"H3"},{"name":"L1"},{"name":"H1"},{"name":"H2"}],[{"name":"H1"},{"name":"H2"},{"name":"L1"},{"name":"S"}],[{"name":"L3"},{"name":"H2"},{"name":"L4"},{"name":"S"}],[{"name":"W"},{"name":"H4"},{"name":"L3"},{"name":"H3"}]]},{"index":1,"type":"expandingWild","reel":4,"rows":[0,1,2,3]},{"index":2,"type":"freeSpinsStart","total":8,"multiplier":1},{"index":3,"type":"freeSpin","current":1,"total":8,"remaining":7},{"index":4,"type":"reveal","board":[[{"name":"W"},{"name":"L1"},{"name":"H2"},{"name":"L2"}],[{"name":"L3"},{"name":"H4"},{"name":"L4"},{"name":"L1"}],[{"name":"S"},{"name":"H4"},{"name":"L4"},{"name":"L2"}],[{"name":"L2"},{"name":"H2"},{"name":"L3"},{"name":"H3"}],[{"name":"H1"},{"name":"L2"},{"name":"H2"},{"name":"W"}]]},{"index":5,"type":"expandingWild","reel":0,"rows":[0,1,2,3]},{"index":6,"type":"expandingWild","reel":4,"rows":[0,1,2,3]},{"index":7,"type":"freeSpin","current":2,"total":8,"remaining":6},{"index":8,"type":"reveal","board":[[{"name":"L4"},{"name":"W"},{"name":"L1"},{"name":"H2"}],[{"name":"H4"},{"name":"L4"},{"name":"L1"},{"name":"H1"}],[{"name":"H1"},{"name":"L2"},{"name":"H2"},{"name":"L3"}],[{"name":"L3"},{"name":"H3"},{"name":"H4"},{"name":"L4"}],[{"name":"H1"},{"name":"H2"},{"name":"L2"},{"name":"H3"}]]},{"index":9,"type":"expandingWild","reel":0,"rows":[0,1,2,3]},{"index":10,"type":"freeSpin","current":3,"total":8,"remaining":5},{"index":11,"type":"reveal","board":[[{"name":"L4"},{"name":"W"},{"name":"L1"},{"name":"H2"}],[{"name":"L3"},{"name":"H4"},{"name":"L4"},{"name":"L1"}],[{"name":"L4"},{"name":"L2"},{"name":"H2"},{"name":"H3"}],[{"name":"L4"},{"name":"H1"},{"name":"L1"},{"name":"W"}],[{"name":"H1"},{"name":"H2"},{"name":"L2"},{"name":"H3"}]]},{"index":12,"type":"expandingWild","reel":0,"rows":[0,1,2,3]},{"index":13,"type":"expandingWild","reel":3,"rows":[0,1,2,3]},{"index":14,"type":"freeSpin","current":4,"total":8,"remaining":4},{"index":15,"type":"reveal","board":[[{"name":"H2"},{"name":"L2"},{"name":"H3"},{"name":"L3"}],[{"name":"H4"},{"name":"L4"},{"name":"L1"},{"name":"H1"}],[{"name":"H3"},{"name":"L3"},{"name":"W"},{"name":"L4"}],[{"name":"H2"},{"name":"L3"},{"name":"H3"},{"name":"L4"}],[{"name":"H4"},{"name":"L3"},{"name":"H3"},{"name":"L1"}]]},{"index":16,"type":"expandingWild","reel":2,"rows":[0,1,2,3]},{"index":17,"type":"freeSpin","current":5,"total":8,"remaining":3},{"index":18,"type":"reveal","board":[[{"name":"L1"},{"name":"H2"},{"name":"L2"},{"name":"H3"}],[{"name":"H2"},{"name":"H3"},{"name":"L1"},{"name":"H1"}],[{"name":"L2"},{"name":"H2"},{"name":"L3"},{"name":"L4"}],[{"name":"H2"},{"name":"L3"},{"name":"H3"},{"name":"L4"}],[{"name":"H1"},{"name":"L2"},{"name":"H2"},{"name":"W"}]]},{"index":19,"type":"expandingWild","reel":4,"rows":[0,1,2,3]},{"index":20,"type":"freeSpin","current":6,"total":8,"remaining":2},{"index":21,"type":"reveal","board":[[{"name":"L2"},{"name":"H4"},{"name":"L4"},{"name":"W"}],[{"name":"L4"},{"name":"L1"},{"name":"H1"},{"name":"L2"}],[{"name":"L3"},{"name":"L4"},{"name":"W"},{"name":"L4"}],[{"name":"S"},{"name":"H1"},{"name":"L3"},{"name":"H3"}],[{"name":"H1"},{"name":"H2"},{"name":"L2"},{"name":"H3"}]]},{"index":22,"type":"expandingWild","reel":0,"rows":[0,1,2,3]},{"index":23,"type":"expandingWild","reel":2,"rows":[0,1,2,3]},{"index":24,"type":"win","positions":[{"reel":1,"row":0},{"reel":0,"row":0},{"reel":0,"row":1},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":2,"row":0},{"reel":2,"row":1},{"reel":2,"row":2},{"reel":2,"row":3}],"amount":20,"symbol":"L4"},{"index":25,"type":"win","positions":[{"reel":1,"row":1},{"reel":0,"row":1},{"reel":0,"row":0},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":2,"row":1},{"reel":2,"row":0},{"reel":2,"row":2},{"reel":2,"row":3}],"amount":50,"symbol":"L1"},{"index":26,"type":"win","positions":[{"reel":1,"row":2},{"reel":0,"row":2},{"reel":0,"row":1},{"reel":0,"row":0},{"reel":0,"row":3},{"reel":2,"row":2},{"reel":2,"row":1},{"reel":3,"row":1},{"reel":2,"row":0},{"reel":2,"row":3}],"amount":500,"symbol":"H1"},{"index":27,"type":"win","positions":[{"reel":1,"row":3},{"reel":0,"row":3},{"reel":0,"row":2},{"reel":0,"row":1},{"reel":0,"row":0},{"reel":2,"row":3},{"reel":2,"row":2},{"reel":2,"row":1},{"reel":2,"row":0}],"amount":40,"symbol":"L2"},{"index":28,"type":"cascade","cascade":1},{"index":29,"type":"removeSymbols","positions":[{"reel":1,"row":0},{"reel":0,"row":0},{"reel":0,"row":1},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":2,"row":0},{"reel":2,"row":1},{"reel":2,"row":2},{"reel":2,"row":3},{"reel":1,"row":1},{"reel":1,"row":2},{"reel":3,"row":1},{"reel":1,"row":3}]},{"index":30,"type":"multiplierIncrease","from":1,"to":2,"reason":"win"},{"index":31,"type":"collapse","board":[[{"name":"empty"},{"name":"empty"},{"name":"empty"},{"name":"empty"}],[{"name":"empty"},{"name":"empty"},{"name":"empty"},{"name":"empty"}],[{"name":"empty"},{"name":"empty"},{"name":"empty"},{"name":"empty"}],[{"name":"empty"},{"name":"S"},{"name":"L3"},{"name":"H3"}],[{"name":"H1"},{"name":"H2"},{"name":"L2"},{"name":"H3"}]]},{"index":32,"type":"refill","board":[[{"name":"S"},{"name":"L4"},{"name":"H1"},{"name":"L3"}],[{"name":"W"},{"name":"H3"},{"name":"L3"},{"name":"H4"}],[{"name":"L1"},{"name":"H1"},{"name":"L2"},{"name":"H2"}],[{"name":"L4"},{"name":"S"},{"name":"L3"},{"name":"H3"}],[{"name":"H1"},{"name":"H2"},{"name":"L2"},{"name":"H3"}]],"positions":[{"reel":0,"row":0},{"reel":0,"row":1},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":1,"row":0},{"reel":1,"row":1},{"reel":1,"row":2},{"reel":1,"row":3},{"reel":2,"row":0},{"reel":2,"row":1},{"reel":2,"row":2},{"reel":2,"row":3},{"reel":3,"row":0}]},{"index":33,"type":"expandingWild","reel":1,"rows":[0,1,2,3]},{"index":34,"type":"freeSpin","current":7,"total":8,"remaining":1},{"index":35,"type":"reveal","board":[[{"name":"L4"},{"name":"W"},{"name":"L1"},{"name":"H2"}],[{"name":"L1"},{"name":"S"},{"name":"L2"},{"name":"H2"}],[{"name":"H2"},{"name":"L1"},{"name":"S"},{"name":"H4"}],[{"name":"L2"},{"name":"L3"},{"name":"H2"},{"name":"L4"}],[{"name":"H4"},{"name":"L3"},{"name":"H3"},{"name":"L1"}]]},{"index":36,"type":"expandingWild","reel":0,"rows":[0,1,2,3]},{"index":37,"type":"freeSpin","current":8,"total":8,"remaining":0},{"index":38,"type":"reveal","board":[[{"name":"H2"},{"name":"L2"},{"name":"H3"},{"name":"L3"}],[{"name":"L1"},{"name":"H1"},{"name":"H2"},{"name":"W"}],[{"name":"L2"},{"name":"H2"},{"name":"H3"},{"name":"L3"}],[{"name":"L3"},{"name":"H2"},{"name":"L4"},{"name":"S"}],[{"name":"L4"},{"name":"H4"},{"name":"L1"},{"name":"H1"}]]},{"index":39,"type":"expandingWild","reel":1,"rows":[0,1,2,3]},{"index":40,"type":"payout","amount":610,"total":610},{"index":41,"type":"roundEnd","payoutMultiplier":610}],"criteria":"freegame","baseGameWins":0.0,"freeGameWins":6.1}') as unknown;

const vaultRound = JSON.parse('{"id":187,"payoutMultiplier":6400,"events":[{"index":0,"type":"reveal","board":[[{"name":"L4"},{"name":"P","value":1000},{"name":"L1"},{"name":"H2"}],[{"name":"L2"},{"name":"P","value":200},{"name":"L3"},{"name":"H4"}],[{"name":"H3"},{"name":"L3"},{"name":"P","value":5000},{"name":"L4"}],[{"name":"H3"},{"name":"L4"},{"name":"H1"},{"name":"L1"}],[{"name":"L2"},{"name":"H2"},{"name":"P","value":200},{"name":"H3"}]]},{"index":1,"type":"holdSpinStart","respins":3,"locked":[{"reel":0,"row":1,"value":1000},{"reel":1,"row":1,"value":200},{"reel":2,"row":2,"value":5000},{"reel":4,"row":2,"value":200}]},{"index":2,"type":"holdSpinRespins","remaining":2},{"index":3,"type":"refill","board":[[{"name":"L2"},{"name":"P","value":1000,"locked":true},{"name":"L3"},{"name":"H4"}],[{"name":"L3"},{"name":"P","value":200,"locked":true},{"name":"L4"},{"name":"L1"}],[{"name":"H3"},{"name":"L3"},{"name":"P","value":5000,"locked":true},{"name":"L4"}],[{"name":"L1"},{"name":"H1"},{"name":"L3"},{"name":"H3"}],[{"name":"H3"},{"name":"L2"},{"name":"P","value":200,"locked":true},{"name":"L4"}]],"positions":[{"reel":0,"row":0},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":1,"row":0},{"reel":1,"row":2},{"reel":1,"row":3},{"reel":2,"row":0},{"reel":2,"row":1},{"reel":2,"row":3},{"reel":3,"row":0},{"reel":3,"row":1},{"reel":3,"row":2},{"reel":3,"row":3},{"reel":4,"row":0},{"reel":4,"row":1},{"reel":4,"row":3}]},{"index":4,"type":"holdSpinRespins","remaining":1},{"index":5,"type":"refill","board":[[{"name":"H1"},{"name":"P","value":1000,"locked":true},{"name":"L2"},{"name":"H4"}],[{"name":"H4"},{"name":"P","value":200,"locked":true},{"name":"L2"},{"name":"L1"}],[{"name":"L4"},{"name":"L1"},{"name":"P","value":5000,"locked":true},{"name":"L2"}],[{"name":"H3"},{"name":"L4"},{"name":"H1"},{"name":"L1"}],[{"name":"H1"},{"name":"H2"},{"name":"P","value":200,"locked":true},{"name":"H3"}]],"positions":[{"reel":0,"row":0},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":1,"row":0},{"reel":1,"row":2},{"reel":1,"row":3},{"reel":2,"row":0},{"reel":2,"row":1},{"reel":2,"row":3},{"reel":3,"row":0},{"reel":3,"row":1},{"reel":3,"row":2},{"reel":3,"row":3},{"reel":4,"row":0},{"reel":4,"row":1},{"reel":4,"row":3}]},{"index":6,"type":"holdSpinRespins","remaining":0},{"index":7,"type":"refill","board":[[{"name":"L1"},{"name":"P","value":1000,"locked":true},{"name":"L2"},{"name":"H3"}],[{"name":"L3"},{"name":"P","value":200,"locked":true},{"name":"L4"},{"name":"L2"}],[{"name":"H1"},{"name":"H3"},{"name":"P","value":5000,"locked":true},{"name":"L3"}],[{"name":"L3"},{"name":"H3"},{"name":"L4"},{"name":"H1"}],[{"name":"L2"},{"name":"L1"},{"name":"P","value":200,"locked":true},{"name":"H4"}]],"positions":[{"reel":0,"row":0},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":1,"row":0},{"reel":1,"row":2},{"reel":1,"row":3},{"reel":2,"row":0},{"reel":2,"row":1},{"reel":2,"row":3},{"reel":3,"row":0},{"reel":3,"row":1},{"reel":3,"row":2},{"reel":3,"row":3},{"reel":4,"row":0},{"reel":4,"row":1},{"reel":4,"row":3}]},{"index":8,"type":"holdSpinEnd","total":6400},{"index":9,"type":"payout","amount":6400,"total":6400},{"index":10,"type":"roundEnd","payoutMultiplier":6400}],"criteria":"holdspin","baseGameWins":64.0,"freeGameWins":0.0}') as unknown;

const vaultLockRound = JSON.parse('{"id":498,"payoutMultiplier":1700,"events":[{"index":0,"type":"reveal","board":[[{"name":"H1"},{"name":"L3"},{"name":"L2"},{"name":"H4"}],[{"name":"P","value":500},{"name":"L3"},{"name":"H4"},{"name":"L4"}],[{"name":"L2"},{"name":"H2"},{"name":"H3"},{"name":"L3"}],[{"name":"L4"},{"name":"L1"},{"name":"H1"},{"name":"L3"}],[{"name":"H1"},{"name":"H2"},{"name":"L2"},{"name":"H3"}]]},{"index":1,"type":"holdSpinStart","respins":3,"locked":[{"reel":1,"row":0,"value":500}]},{"index":2,"type":"holdSpinRespins","remaining":2},{"index":3,"type":"refill","board":[[{"name":"P","value":200,"locked":true},{"name":"L1"},{"name":"H2"},{"name":"L2"}],[{"name":"P","value":500,"locked":true},{"name":"L1"},{"name":"L2"},{"name":"H2"}],[{"name":"L4"},{"name":"P","value":1000,"locked":true},{"name":"L4"},{"name":"H1"}],[{"name":"L2"},{"name":"H4"},{"name":"H2"},{"name":"L4"}],[{"name":"H3"},{"name":"L4"},{"name":"H4"},{"name":"H1"}]],"positions":[{"reel":0,"row":0},{"reel":0,"row":1},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":1,"row":1},{"reel":1,"row":2},{"reel":1,"row":3},{"reel":2,"row":0},{"reel":2,"row":1},{"reel":2,"row":2},{"reel":2,"row":3},{"reel":3,"row":0},{"reel":3,"row":1},{"reel":3,"row":2},{"reel":3,"row":3},{"reel":4,"row":0},{"reel":4,"row":1},{"reel":4,"row":2},{"reel":4,"row":3}]},{"index":4,"type":"holdSpinLock","locks":[{"reel":0,"row":0,"value":200},{"reel":2,"row":1,"value":1000}],"resetRespins":3},{"index":5,"type":"holdSpinRespins","remaining":2},{"index":6,"type":"refill","board":[[{"name":"P","value":200,"locked":true},{"name":"L1"},{"name":"H2"},{"name":"L2"}],[{"name":"P","value":500,"locked":true},{"name":"L2"},{"name":"H2"},{"name":"H3"}],[{"name":"L4"},{"name":"P","value":1000,"locked":true},{"name":"L4"},{"name":"H1"}],[{"name":"L2"},{"name":"H4"},{"name":"H2"},{"name":"L4"}],[{"name":"L4"},{"name":"H4"},{"name":"L1"},{"name":"H1"}]],"positions":[{"reel":0,"row":1},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":1,"row":1},{"reel":1,"row":2},{"reel":1,"row":3},{"reel":2,"row":0},{"reel":2,"row":2},{"reel":2,"row":3},{"reel":3,"row":0},{"reel":3,"row":1},{"reel":3,"row":2},{"reel":3,"row":3},{"reel":4,"row":0},{"reel":4,"row":1},{"reel":4,"row":2},{"reel":4,"row":3}]},{"index":7,"type":"holdSpinRespins","remaining":1},{"index":8,"type":"refill","board":[[{"name":"P","value":200,"locked":true},{"name":"L3"},{"name":"H4"},{"name":"L4"}],[{"name":"P","value":500,"locked":true},{"name":"L3"},{"name":"H4"},{"name":"L4"}],[{"name":"H1"},{"name":"P","value":1000,"locked":true},{"name":"H2"},{"name":"L3"}],[{"name":"H1"},{"name":"L3"},{"name":"H3"},{"name":"H4"}],[{"name":"H3"},{"name":"L4"},{"name":"H4"},{"name":"H1"}]],"positions":[{"reel":0,"row":1},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":1,"row":1},{"reel":1,"row":2},{"reel":1,"row":3},{"reel":2,"row":0},{"reel":2,"row":2},{"reel":2,"row":3},{"reel":3,"row":0},{"reel":3,"row":1},{"reel":3,"row":2},{"reel":3,"row":3},{"reel":4,"row":0},{"reel":4,"row":1},{"reel":4,"row":2},{"reel":4,"row":3}]},{"index":9,"type":"holdSpinRespins","remaining":0},{"index":10,"type":"refill","board":[[{"name":"P","value":200,"locked":true},{"name":"L1"},{"name":"L4"},{"name":"H1"}],[{"name":"P","value":500,"locked":true},{"name":"L2"},{"name":"L1"},{"name":"L2"}],[{"name":"L2"},{"name":"P","value":1000,"locked":true},{"name":"H3"},{"name":"L3"}],[{"name":"L3"},{"name":"H3"},{"name":"L4"},{"name":"H1"}],[{"name":"L4"},{"name":"H4"},{"name":"H1"},{"name":"H2"}]],"positions":[{"reel":0,"row":1},{"reel":0,"row":2},{"reel":0,"row":3},{"reel":1,"row":1},{"reel":1,"row":2},{"reel":1,"row":3},{"reel":2,"row":0},{"reel":2,"row":2},{"reel":2,"row":3},{"reel":3,"row":0},{"reel":3,"row":1},{"reel":3,"row":2},{"reel":3,"row":3},{"reel":4,"row":0},{"reel":4,"row":1},{"reel":4,"row":2},{"reel":4,"row":3}]},{"index":11,"type":"holdSpinEnd","total":1700},{"index":12,"type":"payout","amount":1700,"total":1700},{"index":13,"type":"roundEnd","payoutMultiplier":1700}],"criteria":"holdspin","baseGameWins":17.0,"freeGameWins":0.0}') as unknown;

const ALL_ROUNDS: Record<string, unknown> = {
  base_loss: baseLossRound,
  base_free_spins: baseFreeSpinsRound,
  vault: vaultRound,
  vault_lock: vaultLockRound,
};

describe('parseRoundBook on real SDK book payloads', () => {
  for (const [name, raw] of Object.entries(ALL_ROUNDS)) {
    it(`parses ${name} under the 16-event contract`, () => {
      const round = parseRoundBook(raw);
      expect(round.events.length).toBeGreaterThan(0);
      round.events.forEach((event, position) => {
        expect(event.index).toBe(position);
        expect(CONTRACT_TYPES.has(event.type)).toBe(true);
      });
      expect(round.events[round.events.length - 1].type).toBe('roundEnd');
    });
  }

  it('preserves book id and payoutMultiplier', () => {
    for (const [name, raw] of Object.entries(ALL_ROUNDS)) {
      const round = parseRoundBook(raw);
      expect(round.id).toBeGreaterThanOrEqual(0);
      expect(round.payoutMultiplier).toBeGreaterThanOrEqual(0);
    }
    expect(parseRoundBook(baseFreeSpinsRound).id).toBe(2868);
    expect(parseRoundBook(baseFreeSpinsRound).payoutMultiplier).toBe(610);
    expect(parseRoundBook(vaultRound).id).toBe(187);
    expect(parseRoundBook(vaultRound).payoutMultiplier).toBe(6400);
  });

  it('base free-spins round exposes the cascade family and wild expansion', () => {
    const round = parseRoundBook(baseFreeSpinsRound);
    const types = round.events.map((e) => e.type);
    for (const t of ['reveal', 'win', 'cascade', 'removeSymbols', 'collapse', 'refill', 'expandingWild'] as const) {
      expect(types).toContain(t);
    }
    expect(types).toContain('freeSpinsStart');
    for (let i = 0; i < 8; i += 1) expect(types).toContain('freeSpin');
    // multiplier advances once when a free-spin win occurs
    expect(round.events.filter((e) => e.type === 'multiplierIncrease')).toHaveLength(1);
    const first = round.events.find((e) => e.type === 'freeSpinsStart');
    const multiplier = round.events.find((e) => e.type === 'multiplierIncrease');
    expect(first).toBeDefined();
    if (multiplier && multiplier.type === 'multiplierIncrease') {
      expect(multiplier.from).toBe(1);
      expect(multiplier.to).toBe(2);
    }
  });

  it('vault rounds expose the hold & spin family', () => {
    for (const [name, raw] of Object.entries({ vault: vaultRound, vault_lock: vaultLockRound })) {
      const round = parseRoundBook(raw);
      const types = round.events.map((e) => e.type);
      expect(types).toContain('holdSpinStart');
      expect(types).toContain('holdSpinRespins');
      expect(types).toContain('holdSpinEnd');
      expect(types).toContain('refill');
      const start = round.events.find((e) => e.type === 'holdSpinStart');
      expect(start).toBeDefined();
      if (start && start.type === 'holdSpinStart') {
        expect(start.respins).toBeGreaterThanOrEqual(3);
        expect(start.locked.length).toBeGreaterThan(0);
        // every locked cell carries reel/row/value
        for (const cell of start.locked) {
          expect(Number.isInteger(cell.reel)).toBe(true);
          expect(Number.isInteger(cell.row)).toBe(true);
          expect(Number.isInteger(cell.value)).toBe(true);
        }
      }
    }
    // only the vault_lock round carries a new lock landing during respins
    expect(parseRoundBook(vaultLockRound).events.map((e) => e.type)).toContain('holdSpinLock');
  });

  it('reports the final payout consistently (payout.total === roundEnd.payoutMultiplier)', () => {
    for (const [name, raw] of Object.entries(ALL_ROUNDS)) {
      const round = parseRoundBook(raw);
      const payouts = round.events.filter((e) => e.type === 'payout') as PayoutEvent[];
      const last = round.events[round.events.length - 1] as RoundEndEvent;
      expect(payouts).toHaveLength(1);
      expect(payouts[0].total).toBe(last.payoutMultiplier);
      expect(payouts[0].amount).toBeGreaterThanOrEqual(0);
    }
  });

  it('rejects non-contract event types and broken indices', () => {
    const good = JSON.parse(JSON.stringify(baseLossRound)) as { events: Array<Record<string, unknown>> };
    expect(() => parseRoundBook({ ...good, events: [{ index: 0, type: 'notAThing' }] })).toThrow(/Unsupported RGS event/);
    expect(() => parseRoundBook({ ...good, events: [{ index: 1, type: 'reveal' }] })).toThrow(/Invalid RGS event index/);
  });
});
