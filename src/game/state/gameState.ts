import { GAME_CONFIG } from '../config/gameConfig';
import type { Board, GameEvent, Position } from '../events/types';

export type LockedSymbol = Position & { value: number; multiplier: number };

export type GameState = {
  board: Board;
  phase: 'idle' | 'base' | 'cascade' | 'freeSpins' | 'holdSpin' | 'complete';
  win: number;
  totalWin: number;
  cascade: number;
  freeSpins: { active: boolean; current: number; total: number; remaining: number; multiplier: number };
  holdSpin: { active: boolean; respins: number; locked: Record<string, LockedSymbol>; total: number };
  lastEventIndex: number;
};

export function emptyBoard(): Board {
  return Array.from({ length: GAME_CONFIG.columns }, () =>
    Array.from({ length: GAME_CONFIG.rows }, () => ({ name: 'cash' }))
  );
}

export function initialGameState(board: Board = emptyBoard()): GameState {
  return {
    board, phase: 'idle', win: 0, totalWin: 0, cascade: 0, lastEventIndex: -1,
    freeSpins: { active: false, current: 0, total: 0, remaining: 0, multiplier: 1 },
    holdSpin: { active: false, respins: 0, locked: {}, total: 0 }
  };
}

const key = ({ reel, row }: Position) => `${reel}:${row}`;
const copyBoard = (board: Board) => board.map((reel) => reel.map((symbol) => ({ ...symbol })));

export function reduceGameEvent(state: GameState, event: GameEvent): GameState {
  if (event.index <= state.lastEventIndex) throw new Error(`Non-monotonic event index ${event.index}`);
  const next: GameState = { ...state, lastEventIndex: event.index };

  switch (event.type) {
    case 'reveal': return { ...next, board: copyBoard(event.board), phase: state.freeSpins.active ? 'freeSpins' : 'base', win: 0 };
    case 'win': return { ...next, win: event.amount, totalWin: state.totalWin + event.amount };
    case 'cascade': return { ...next, phase: 'cascade', cascade: event.cascade };
    case 'removeSymbols': {
      const board = copyBoard(state.board);
      event.positions.forEach(({ reel, row }) => { if (board[reel]?.[row]) board[reel][row] = { name: 'empty' }; });
      return { ...next, board };
    }
    case 'collapse':
    case 'refill': return { ...next, board: copyBoard(event.board) };
    case 'expandingWild': {
      const board = copyBoard(state.board);
      (event.rows ?? Array.from({ length: GAME_CONFIG.rows }, (_, row) => row)).forEach((row) => {
        if (board[event.reel]?.[row]) board[event.reel][row] = { name: 'wild' };
      });
      return { ...next, board };
    }
    case 'freeSpinsStart': return {
      ...next, phase: 'freeSpins',
      freeSpins: { active: true, current: 0, total: event.total, remaining: event.total, multiplier: event.multiplier }
    };
    case 'freeSpin': return { ...next, phase: 'freeSpins', freeSpins: { ...state.freeSpins, active: true, ...event } };
    case 'multiplierIncrease': {
      const allowed = GAME_CONFIG.freeSpins.multiplierProgression as readonly number[];
      if (!allowed.includes(event.to) || event.to < state.freeSpins.multiplier) throw new Error(`Invalid multiplier ${event.to}`);
      return { ...next, freeSpins: { ...state.freeSpins, multiplier: event.to } };
    }
    case 'holdSpinStart': {
      const locked = Object.fromEntries(event.locked.map((item) => [key(item), { ...item, multiplier: item.multiplier ?? 1 }]));
      return { ...next, phase: 'holdSpin', holdSpin: { active: true, respins: event.respins, locked, total: 0 } };
    }
    case 'holdSpinLock': {
      const locked = { ...state.holdSpin.locked };
      event.locks.forEach((item) => { locked[key(item)] = { ...item, multiplier: item.multiplier ?? 1 }; });
      return { ...next, phase: 'holdSpin', holdSpin: { ...state.holdSpin, active: true, locked, respins: event.resetRespins ?? state.holdSpin.respins } };
    }
    case 'holdSpinRespins': return { ...next, holdSpin: { ...state.holdSpin, respins: event.remaining } };
    case 'holdSpinEnd': return { ...next, phase: 'base', holdSpin: { ...state.holdSpin, active: false, total: event.total } };
    case 'payout': return { ...next, win: event.amount, totalWin: event.total };
    case 'roundEnd': return {
      ...next, phase: 'complete',
      freeSpins: { ...state.freeSpins, active: false },
      holdSpin: { ...state.holdSpin, active: false }
    };
  }
}
