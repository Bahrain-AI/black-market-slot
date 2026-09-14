export const API_AMOUNT_MULTIPLIER = 1_000_000;

export type EngineConfig = {
  minBet: number;
  maxBet: number;
  stepBet: number;
  defaultBetLevel: number;
  betLevels?: number[];
  jurisdiction?: {
    socialCasino?: boolean;
    disabledFullscreen?: boolean;
    disabledTurbo?: boolean;
    [key: string]: unknown;
  };
};

export type AuthenticateResponse = {
  balance: { amount: number; currency: string };
  config: EngineConfig;
  round?: Record<string, unknown> | null;
  error?: unknown;
};

export type PlayResponse = {
  balance?: { amount: number; currency: string };
  round?: Record<string, unknown>;
  error?: unknown;
};

function trimSlash(value: string) {
  return value.replace(/\/+$/, '');
}

async function post<T>(base: string, path: string, body: unknown): Promise<T> {
  const response = await fetch(`${trimSlash(base)}${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw Object.assign(new Error(data?.message || `RGS ${response.status}`), { data });
  return data as T;
}

export function readEngineParams() {
  const q = new URLSearchParams(location.search);
  return {
    sessionID: q.get('sessionID') || '',
    rgsUrl: q.get('rgs_url') || '',
    lang: q.get('lang') || 'en',
    device: q.get('device') || 'desktop',
    replay: q.get('replay') === 'true',
    game: q.get('game') || '',
    version: q.get('version') || '',
    mode: q.get('mode') || 'base',
    event: q.get('event') || '',
    currency: q.get('currency') || 'USD',
    amount: Number(q.get('amount') || 0),
    social: q.get('social') === 'true'
  };
}

export function authenticate(rgsUrl: string, sessionID: string) {
  return post<AuthenticateResponse>(rgsUrl, '/wallet/authenticate', { sessionID });
}

export function play(rgsUrl: string, sessionID: string, amount: number, mode = 'base') {
  return post<PlayResponse>(rgsUrl, '/wallet/play', { sessionID, amount, mode });
}

export function endRound(rgsUrl: string, sessionID: string) {
  return post<{ balance?: { amount: number; currency: string } }>(rgsUrl, '/wallet/end-round', { sessionID });
}

export async function getReplay(rgsUrl: string, game: string, version: string, mode: string, event: string) {
  const url = `${trimSlash(rgsUrl)}/bet/replay/${encodeURIComponent(game)}/${encodeURIComponent(version)}/${encodeURIComponent(mode)}/${encodeURIComponent(event)}`;
  const response = await fetch(url);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data?.message || `Replay ${response.status}`);
  return data;
}

export function formatEngineAmount(amount: number, currency = 'USD', forcePrecision = false) {
  const value = amount / API_AMOUNT_MULTIPLIER;
  const max = forcePrecision && value < 0.1 ? 4 : value < 1 ? 3 : 2;
  try {
    return new Intl.NumberFormat('en', {
      style: 'currency',
      currency,
      minimumFractionDigits: Math.min(2, max),
      maximumFractionDigits: max
    }).format(value);
  } catch {
    return `${currency} ${value.toFixed(max)}`;
  }
}
