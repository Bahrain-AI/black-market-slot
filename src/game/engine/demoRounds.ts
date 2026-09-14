import type { Board, RoundBook, SymbolData } from '../events/types';

const names = ['watch', 'diamond', 'ace', 'gold', 'cash', 'passport', 'bag', 'bust', 'wild', 'vip'];
const board = (offset = 0): Board => Array.from({ length: 5 }, (_, reel) =>
  Array.from({ length: 4 }, (_, row): SymbolData => ({ name: names[(reel * 4 + row + offset) % names.length] }))
);

const first = board();
const refill = board(3);

export const DEMO_ROUNDS: RoundBook[] = [{
  id: 1,
  payoutMultiplier: 1200,
  events: [
    { index: 0, type: 'reveal', board: first },
    { index: 1, type: 'win', positions: [{ reel: 0, row: 0 }, { reel: 1, row: 0 }, { reel: 2, row: 0 }], amount: 200 },
    { index: 2, type: 'cascade', cascade: 1 },
    { index: 3, type: 'removeSymbols', positions: [{ reel: 0, row: 0 }, { reel: 1, row: 0 }, { reel: 2, row: 0 }] },
    { index: 4, type: 'collapse', board: refill },
    { index: 5, type: 'refill', board: refill },
    { index: 6, type: 'freeSpinsStart', total: 3, multiplier: 1 },
    { index: 7, type: 'freeSpin', current: 1, total: 3, remaining: 2 },
    { index: 8, type: 'reveal', board: board(4) },
    { index: 9, type: 'expandingWild', reel: 2 },
    { index: 10, type: 'win', positions: [{ reel: 2, row: 0 }, { reel: 2, row: 1 }, { reel: 2, row: 2 }, { reel: 2, row: 3 }], amount: 500 },
    { index: 11, type: 'multiplierIncrease', from: 1, to: 2, reason: 'cascade' },
    { index: 12, type: 'freeSpin', current: 2, total: 3, remaining: 1 },
    { index: 13, type: 'multiplierIncrease', from: 2, to: 3, reason: 'win' },
    { index: 14, type: 'freeSpin', current: 3, total: 3, remaining: 0 },
    { index: 15, type: 'holdSpinStart', respins: 3, locked: [{ reel: 0, row: 0, value: 200 }] },
    { index: 16, type: 'holdSpinRespins', remaining: 2 },
    { index: 17, type: 'holdSpinLock', resetRespins: 3, locks: [{ reel: 3, row: 2, value: 500, multiplier: 2 }] },
    { index: 18, type: 'holdSpinRespins', remaining: 2 },
    { index: 19, type: 'holdSpinEnd', total: 1000 },
    { index: 20, type: 'payout', amount: 1200, total: 1200 },
    { index: 21, type: 'roundEnd', payoutMultiplier: 1200 }
  ]
}];
