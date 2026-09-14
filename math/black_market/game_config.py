from dataclasses import dataclass, field

TARGET_RTP = 0.96  # Provisional tuning target; not certified.
DEFAULT_MAX_WIN = 5_000.0


@dataclass(frozen=True)
class BetMode:
    name: str
    cost: float


@dataclass(frozen=True)
class GameConfig:
    game_id: str = "black-market"
    columns: int = 5
    rows: int = 4
    target_rtp: float = TARGET_RTP
    max_win: float = DEFAULT_MAX_WIN
    multiplier_progression: tuple[int, ...] = (1, 2, 3, 5, 10)
    symbols: tuple[str, ...] = ("watch", "diamond", "ace", "gold", "cash", "passport", "bag", "bust", "wild", "scatter")
    special_symbols: dict[str, tuple[str, ...]] = field(default_factory=lambda: {"wild": ("wild",), "scatter": ("scatter",)})
    bet_modes: tuple[BetMode, ...] = (
        BetMode("base", 1.0),
        BetMode("backroom", 60.0),
        BetMode("vault", 100.0),
        BetMode("black_card", 200.0),
    )

    def validate(self) -> None:
        if (self.columns, self.rows) != (5, 4):
            raise ValueError("BLACK MARKET Phase 1 requires a 5x4 board")
        if not 0 < self.target_rtp < 1:
            raise ValueError("target_rtp must be a provisional ratio between 0 and 1")
        if self.multiplier_progression[0] != 1 or sorted(set(self.multiplier_progression)) != list(self.multiplier_progression):
            raise ValueError("multiplier progression must be strictly increasing from 1")
