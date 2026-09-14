import type { GameEvent, RoundBook } from '../events/types';

const EVENT_TYPES = new Set<GameEvent['type']>([
  'reveal', 'win', 'cascade', 'removeSymbols', 'collapse', 'refill', 'expandingWild',
  'freeSpinsStart', 'freeSpin', 'multiplierIncrease', 'holdSpinStart', 'holdSpinLock',
  'holdSpinRespins', 'holdSpinEnd', 'payout', 'roundEnd'
]);

export function parseRoundBook(input: unknown): RoundBook {
  const value = input as Record<string, unknown>;
  if (!value || !Array.isArray(value.events)) throw new Error('RGS round is missing events');
  const events = value.events as Array<Record<string, unknown>>;
  events.forEach((event, position) => {
    if (!EVENT_TYPES.has(event.type as GameEvent['type'])) throw new Error(`Unsupported RGS event: ${String(event.type)}`);
    if (!Number.isInteger(event.index) || event.index !== position) throw new Error(`Invalid RGS event index at ${position}`);
  });
  return {
    id: Number(value.id ?? 0),
    events: events as GameEvent[],
    payoutMultiplier: Number(value.payoutMultiplier ?? 0)
  };
}
