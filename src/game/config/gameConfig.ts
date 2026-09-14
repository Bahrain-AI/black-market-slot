export const GAME_CONFIG = {
  columns: 5,
  rows: 4,
  freeSpins: {
    multiplierProgression: [1, 2, 3, 5, 10] as const
  },
  timing: {
    normal: 260,
    turbo: 80
  }
} as const;

export type GameConfig = typeof GAME_CONFIG;
