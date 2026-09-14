from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .game_config import GameConfig


@dataclass
class GameState:
    config: GameConfig
    board: list[list[dict]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    total_win: float = 0.0
    multiplier: int = 1
    locked: dict[tuple[int, int], dict] = field(default_factory=dict)
    respins: int = 0

    def emit(self, value: dict[str, Any]) -> dict[str, Any]:
        indexed = {"index": len(self.events), **deepcopy(value)}
        self.events.append(indexed)
        return indexed

    def reset_round(self) -> None:
        self.board = []
        self.events = []
        self.total_win = 0.0
        self.multiplier = self.config.multiplier_progression[0]
        self.locked = {}
        self.respins = 0

    def book(self, simulation_id: int) -> dict[str, Any]:
        # Stake Engine result books encode payout multipliers in hundredths.
        # Keeping this as an integer prevents float drift between books and LUTs.
        payout_multiplier = int(round(self.total_win * 100))
        return {"id": simulation_id, "events": deepcopy(self.events), "payoutMultiplier": payout_multiplier}
