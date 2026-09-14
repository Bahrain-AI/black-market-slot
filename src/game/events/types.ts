export type Position = { reel: number; row: number };
export type SymbolData = { name: string; value?: number; multiplier?: number; locked?: boolean };
export type Board = SymbolData[][];

type Indexed<T extends string> = { index: number; type: T };

export type RevealEvent = Indexed<'reveal'> & { board: Board };
export type WinEvent = Indexed<'win'> & { positions: Position[]; amount: number; symbol?: string };
export type CascadeEvent = Indexed<'cascade'> & { cascade: number };
export type RemoveSymbolsEvent = Indexed<'removeSymbols'> & { positions: Position[] };
export type CollapseEvent = Indexed<'collapse'> & { board: Board };
export type RefillEvent = Indexed<'refill'> & { board: Board; positions?: Position[] };
export type ExpandingWildEvent = Indexed<'expandingWild'> & { reel: number; rows?: number[] };
export type FreeSpinsStartEvent = Indexed<'freeSpinsStart'> & { total: number; multiplier: number };
export type FreeSpinEvent = Indexed<'freeSpin'> & { current: number; total: number; remaining: number };
export type MultiplierIncreaseEvent = Indexed<'multiplierIncrease'> & { from: number; to: number; reason: 'win' | 'cascade' };
export type HoldSpinStartEvent = Indexed<'holdSpinStart'> & { respins: number; locked: Array<Position & { value: number; multiplier?: number }> };
export type HoldSpinLockEvent = Indexed<'holdSpinLock'> & { locks: Array<Position & { value: number; multiplier?: number }>; resetRespins?: number };
export type HoldSpinRespinsEvent = Indexed<'holdSpinRespins'> & { remaining: number };
export type HoldSpinEndEvent = Indexed<'holdSpinEnd'> & { total: number };
export type PayoutEvent = Indexed<'payout'> & { amount: number; total: number };
export type RoundEndEvent = Indexed<'roundEnd'> & { payoutMultiplier: number };

export type GameEvent =
  | RevealEvent | WinEvent | CascadeEvent | RemoveSymbolsEvent | CollapseEvent | RefillEvent
  | ExpandingWildEvent | FreeSpinsStartEvent | FreeSpinEvent | MultiplierIncreaseEvent
  | HoldSpinStartEvent | HoldSpinLockEvent | HoldSpinRespinsEvent | HoldSpinEndEvent
  | PayoutEvent | RoundEndEvent;

export type RoundBook = { id: number; events: GameEvent[]; payoutMultiplier: number };
