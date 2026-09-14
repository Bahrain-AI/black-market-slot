import { afterEach, describe, expect, it, vi } from 'vitest';
import { getReplay, payoutFromHundredths, play } from './rgs';

afterEach(() => vi.unstubAllGlobals());

describe('Stake RGS transport', () => {
  it('converts 610 and 6400 SDK payout hundredths at the wallet boundary', () => {
    expect(payoutFromHundredths(1_000_000, 610)).toBe(6_100_000);
    expect(payoutFromHundredths(1_000_000, 6400)).toBe(64_000_000);
  });

  it('preserves integer amount precision in wallet play', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ balance: { amount: 42_000_001, currency: 'USD' }, round: { id: 1, events: [], payoutMultiplier: 0 } }), { status: 200 }));
    vi.stubGlobal('fetch', fetchMock);
    await play('https://rgs.example/', 'session', 1_000_001, 'base');
    expect(fetchMock).toHaveBeenCalledWith('https://rgs.example/wallet/play', expect.objectContaining({ body: JSON.stringify({ sessionID: 'session', amount: 1_000_001, mode: 'base' }) }));
  });

  it('loads deterministic replay data without wallet play', async () => {
    const book = { id: 7, events: [{ index: 0, type: 'roundEnd', payoutMultiplier: 0 }], payoutMultiplier: 0 };
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(book), { status: 200 }));
    vi.stubGlobal('fetch', fetchMock);
    await expect(getReplay('https://rgs.example', 'black market', '1', 'base', 'event/7')).resolves.toEqual(book);
    expect(fetchMock).toHaveBeenCalledWith('https://rgs.example/bet/replay/black%20market/1/base/event%2F7');
  });
});
