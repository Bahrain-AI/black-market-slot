import { describe, expect, it } from 'vitest';
import { initialGameState, reduceGameEvent } from './gameState';
import type { GameEvent } from '../events/types';

function apply(events: GameEvent[]) { return events.reduce(reduceGameEvent, initialGameState()); }

describe('Stake event state', () => {
  it('plays cascade removal, collapse and refill in order', () => {
    const board = Array.from({ length: 5 }, () => Array.from({ length: 4 }, () => ({ name: 'cash' })));
    const events: GameEvent[] = [
      { index: 0, type: 'reveal', board },
      { index: 1, type: 'win', positions: [{ reel: 0, row: 0 }], amount: 2 },
      { index: 2, type: 'cascade', cascade: 1 },
      { index: 3, type: 'removeSymbols', positions: [{ reel: 0, row: 0 }] },
      { index: 4, type: 'collapse', board },
      { index: 5, type: 'refill', board }
    ];
    const state = apply(events);
    expect(state.cascade).toBe(1);
    expect(state.board[0][0].name).toBe('cash');
    expect(state.totalWin).toBe(2);
  });

  it('expands a wild and advances the configured free-spin multiplier', () => {
    const state = apply([
      { index: 0, type: 'freeSpinsStart', total: 8, multiplier: 1 },
      { index: 1, type: 'freeSpin', current: 1, total: 8, remaining: 7 },
      { index: 2, type: 'expandingWild', reel: 2 },
      { index: 3, type: 'multiplierIncrease', from: 1, to: 2, reason: 'cascade' }
    ]);
    expect(state.board[2].every((symbol) => symbol.name === 'wild')).toBe(true);
    expect(state.freeSpins).toMatchObject({ active: true, current: 1, remaining: 7, multiplier: 2 });
  });

  it('persists hold-and-spin locks and updates existing values', () => {
    const state = apply([
      { index: 0, type: 'holdSpinStart', respins: 3, locked: [{ reel: 0, row: 0, value: 1 }] },
      { index: 1, type: 'holdSpinRespins', remaining: 2 },
      { index: 2, type: 'holdSpinLock', resetRespins: 3, locks: [{ reel: 2, row: 1, value: 5 }, { reel: 0, row: 0, value: 2, multiplier: 2 }] },
      { index: 3, type: 'holdSpinRespins', remaining: 2 }
    ]);
    expect(Object.keys(state.holdSpin.locked)).toHaveLength(2);
    expect(state.holdSpin.locked['0:0']).toMatchObject({ value: 2, multiplier: 2 });
    expect(state.holdSpin.locked['2:1'].value).toBe(5);
    expect(state.holdSpin.respins).toBe(2);
  });

  it('rejects non-deterministic event ordering', () => {
    const state = reduceGameEvent(initialGameState(), { index: 1, type: 'payout', amount: 0, total: 0 });
    expect(() => reduceGameEvent(state, { index: 1, type: 'roundEnd', payoutMultiplier: 0 })).toThrow(/Non-monotonic/);
  });
});
