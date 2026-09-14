// BLACK MARKET in-game rules / game-information copy.
//
// Single source of truth for the Rules modal. Values mirror the provisional
// math configuration in `math/black_market/game_config.py` and the SDK overlay
// (`math/sdk_game/black_market/`). They are PROVISIONAL tuning values and must
// be replaced from the approved/certified math package before submission.
// Nothing in this file is certified production math.

export interface BetModeInfo {
  name: string;
  label: string;
  cost: number;
  buyBonus: boolean;
  description: string;
}

export interface GameRules {
  gameId: string;
  title: string;
  format: string;
  features: string[];
  progression: number[];
  targetRtp: number; // provisional
  maxWin: number; // provisional (bet multiples)
  provisional: boolean;
  betModes: BetModeInfo[];
  controls: string;
}

export const GAME_RULES: GameRules = {
  gameId: 'black-market',
  title: 'BLACK MARKET',
  format: '5×4 cascading reels',
  features: [
    'Cascading wins with expanding Wilds',
    'Free Spins with a progressive multiplier (1× → 2× → 3× → 5× → 10×)',
    'Hold & Spin with locked prize symbols',
    'Buy Bonus modes: Back Room (Free Spins), Vault (Hold & Spin), Black Card (Free Spins + Hold & Spin)',
  ],
  progression: [1, 2, 3, 5, 10],
  targetRtp: 0.96, // PROVISIONAL tuning target, not certified
  maxWin: 5000, // PROVISIONAL (bet multiples), not certified
  provisional: true,
  betModes: [
    { name: 'base', label: 'Base', cost: 1, buyBonus: false, description: 'Base game with natural Free Spins and Hold & Spin triggers.' },
    { name: 'backroom', label: 'Back Room', cost: 60, buyBonus: true, description: 'Buy directly into Free Spins.' },
    { name: 'vault', label: 'Vault', cost: 100, buyBonus: true, description: 'Buy directly into Hold & Spin.' },
    { name: 'black_card', label: 'Black Card', cost: 200, buyBonus: true, description: 'Buy Free Spins plus Hold & Spin.' },
  ],
  controls:
    'Spin places a bet. Bet controls use only levels supplied by the RGS. Turbo changes presentation speed when the jurisdiction permits it. Spacebar activates Spin.',
};