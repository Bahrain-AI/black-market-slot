"""Seeded provisional round simulator for BLACK MARKET.

PROVISIONAL ONLY. This module drives the phase-1 deterministic event contract
(``GameExecutables`` / ``GameState``) to produce development-scale result books
so the full Stake Engine publication pipeline (books, lookups, index, Zstandard,
validation, PAR-style statistics, replay records) can be exercised end to end.

Rules implemented here are provisional tuning rules, not approved production
math. Every probability, pay value, feature trigger and reel weight must be
replaced by the certified simulation set before any official submission. The
simulator intentionally mirrors the provisional values in
``math/sdk_game/black_market/game_config.py`` and must be kept in sync with it.

The simulator is part of the math layer: it is the generator that feeds the
frontend event contract. It contains no frontend RNG and never runs in the
browser.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Iterator

from .game_config import GameConfig
from .game_executables import GameExecutables
from .gamestate import GameState

# --- Provisional constants (mirror math/sdk_game/black_market/game_config.py) ---

PAY_SYMBOLS = ("H1", "H2", "H3", "H4", "L1", "L2", "L3", "L4")
WILD = "W"
SCATTER = "S"
PRIZE = "P"
EMPTY = "empty"

# Winning cluster size bands and per-band bet-multiple payout, from the overlay.
PAY_RANGES: tuple[tuple[int, int], ...] = ((8, 9), (10, 11), (12, 14), (15, 20))
PAY_VALUES: dict[str, tuple[float, ...]] = {
    "H1": (2.0, 5.0, 12.0, 35.0),
    "H2": (1.5, 4.0, 9.0, 25.0),
    "H3": (1.0, 3.0, 7.0, 18.0),
    "H4": (0.8, 2.0, 5.0, 14.0),
    "L1": (0.5, 1.2, 3.0, 8.0),
    "L2": (0.4, 1.0, 2.5, 6.0),
    "L3": (0.3, 0.8, 2.0, 5.0),
    "L4": (0.2, 0.6, 1.5, 4.0),
}

# Provisional feature configuration.
SCATTER_FREE_SPINS = {3: 8, 4: 10, 5: 12}  # base-game 3/4/5 scatters -> spins
SCATTER_RETRIGGER = {3: 3, 4: 5, 5: 8}  # free-spin retriggers
HOLD_SPIN_TRIGGER = 6  # minimum prize symbols to trigger Hold & Spin
HOLD_SPIN_RESPINS = 3
HOLD_SPIN_RESET = 3
PRIZE_MIN, PRIZE_MAX = 1, 10  # provisional prize values (bet multiples)
WINCAP_FREQUENCY = 0.001  # provisional forced max-win share (overlay "wincap" quota)
BLACK_CARD_START = 3  # boosted starting multiplier for black_card

BOARD_REELS = 5
BOARD_ROWS = 4
FULL_LOCK = BOARD_REELS * BOARD_ROWS

REEL_DECK_NAMES = ("BR0", "FR0", "HR0")


def _read_reel_strips(path: Path) -> list[list[str]]:
    """Read an SDK-style reel CSV into a list of one strip per reel (columns)."""
    strips: list[list[str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for row_number, line in enumerate(handle):
            columns = line.strip().split(",")
            for index, raw in enumerate(columns):
                symbol = "".join(ch for ch in raw if ch.strip().isalnum())
                if not symbol:
                    raise ValueError(f"empty symbol in {path.name} row {row_number + 1}")
                if row_number == 0:
                    strips.append([symbol])
                else:
                    strips[index].append(symbol)
    return strips


class ReelDecks:
    """Provisional reel decks: each reel draw is a uniform random row pick."""

    def __init__(self, overlay_reels: Path, rng: random.Random):
        self.rng = rng
        self.decks: dict[str, list[list[str]]] = {}
        for name in REEL_DECK_NAMES:
            self.decks[name] = _read_reel_strips(overlay_reels / f"{name}.csv")
        for name, strips in self.decks.items():
            if len(strips) != BOARD_REELS:
                raise ValueError(f"reel strip {name} must define exactly {BOARD_REELS} reels")
            if any(len(strip) < BOARD_ROWS for strip in strips):
                raise ValueError(f"reel strip {name} has a column shorter than {BOARD_ROWS} symbols")

    def draw(self, deck_name: str) -> list[list[dict]]:
        """Draw one 5x4 board, reel-major, from the named deck."""
        strips = self.decks[deck_name]
        return [
            [{"name": strips[reel][self.rng.randrange(len(strips[reel]))]} for _ in range(BOARD_ROWS)]
            for reel in range(BOARD_REELS)
        ]


def find_clusters(board: list[list[dict]]) -> list[dict]:
    """Return pay-anywhere clusters of >= 8 connected matching symbols (wilds substitute).

    Each returned dict has ``symbol``, ``count``, ``band``, ``amount`` (bet
    multiples) and ``positions``. Wild-reel expansion is handled by the caller.
    """
    clusters: list[dict] = []
    seen: set[tuple[int, int]] = set()
    for reel in range(BOARD_REELS):
        for row in range(BOARD_ROWS):
            if (reel, row) in seen:
                continue
            seed = board[reel][row]["name"]
            if seed in (EMPTY, WILD) or seed not in PAY_SYMBOLS:
                continue
            stack = [(reel, row)]
            members: list[tuple[int, int]] = []
            while stack:
                current_reel, current_row = stack.pop()
                if (current_reel, current_row) in seen:
                    continue
                cell = board[current_reel][current_row]["name"]
                if cell not in (seed, WILD):
                    continue
                seen.add((current_reel, current_row))
                members.append((current_reel, current_row))
                for delta_reel, delta_row in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    near_reel, near_row = current_reel + delta_reel, current_row + delta_row
                    if 0 <= near_reel < BOARD_REELS and 0 <= near_row < BOARD_ROWS:
                        stack.append((near_reel, near_row))
            if len(members) >= 8:
                band = next(
                    index for index, (low, high) in enumerate(PAY_RANGES) if low <= len(members) <= high
                )
                clusters.append(
                    {
                        "symbol": seed,
                        "count": len(members),
                        "band": band,
                        "amount": PAY_VALUES[seed][band],
                        "positions": [{"reel": r, "row": c} for r, c in sorted(members)],
                    }
                )
    return clusters


def count_symbols(board: list[list[dict]], name: str) -> int:
    return sum(1 for reel in board for cell in reel if cell["name"] == name)


def _random_prize_value(rng: random.Random) -> int:
    return rng.randint(PRIZE_MIN, PRIZE_MAX)


def _wild_reels(board: list[list[dict]], cluster: dict) -> list[int]:
    """Reels expanded because the winning cluster contains a Wild symbol."""
    expanded: set[int] = set()
    for position in cluster["positions"]:
        if board[position["reel"]][position["row"]]["name"] == WILD:
            expanded.add(position["reel"])
    return sorted(expanded)


class Simulator:
    """Seeded provisional round generator for one bet mode."""

    def __init__(self, config: GameConfig, mode_name: str, overlay_reels: Path, seed: int):
        if mode_name not in {mode.name for mode in config.bet_modes}:
            raise ValueError(f"unknown bet mode: {mode_name}")
        self.config = config
        self.mode_name = mode_name
        self.overlay_reels = overlay_reels
        self.rng = random.Random(seed)

    def rounds(self, count: int, start_id: int = 0) -> Iterator[dict]:
        """Yield ``count`` sequential books with ids ``start_id .. start_id+count-1``."""
        decks = ReelDecks(self.overlay_reels, self.rng)
        for offset in range(count):
            yield self._round(decks, start_id + offset)

    # --- single round -------------------------------------------------------

    def _round(self, decks: ReelDecks, simulation_id: int) -> dict:
        state = GameState(self.config)
        game = GameExecutables(state)
        forced = {
            "base": "natural",
            "backroom": "free_spins",
            "vault": "hold_spin",
            "black_card": "hybrid",
        }[self.mode_name]

        if forced == "natural":
            if self.rng.random() < WINCAP_FREQUENCY:
                self._forced_wincap(game)
            else:
                game.reveal(decks.draw("BR0"))
                self._play_cascades(game, decks, in_free_spins=False)
                scatters = count_symbols(state.board, SCATTER)
                prizes = count_symbols(state.board, PRIZE)
                if scatters >= 3:
                    self._play_free_spins(game, decks, SCATTER_FREE_SPINS[min(scatters, 5)])
                elif prizes >= HOLD_SPIN_TRIGGER:
                    self._play_hold_spin(game, decks, initial=True)
        elif forced == "free_spins":
            self._play_free_spins(game, decks, 8)
        elif forced == "hold_spin":
            self._play_hold_spin(game, decks, initial=True)
        elif forced == "hybrid":
            self._play_free_spins(game, decks, 8, boosted_multiplier=BLACK_CARD_START)
            self._play_hold_spin(game, decks, initial=False)

        game.end_round()
        return state.book(simulation_id)

    def _forced_wincap(self, game: GameExecutables) -> None:
        """Force a provisional max-win round (mirrors the overlay 'wincap' quota)."""
        board = [[{"name": WILD} for _ in range(BOARD_ROWS)] for _ in range(BOARD_REELS)]
        game.reveal(board)
        positions = [{"reel": reel, "row": row} for reel in range(BOARD_REELS) for row in range(BOARD_ROWS)]
        game.cascade(positions, board, self.config.max_win, "H1", 1)

    # --- cascade resolver ---------------------------------------------------

    def _play_cascades(self, game: GameExecutables, decks: ReelDecks, *, in_free_spins: bool) -> None:
        number = 0
        while True:
            clusters = find_clusters(game.state.board)
            if not clusters:
                return
            cluster = clusters[0]
            number += 1
            for reel in _wild_reels(game.state.board, cluster):
                game.expanding_wild(reel)
            deck = "FR0" if in_free_spins else "BR0"
            game.cascade(
                cluster["positions"],
                decks.draw(deck),
                cluster["amount"],
                cluster["symbol"],
                number,
            )
            if in_free_spins:
                game.advance_multiplier("cascade")

    # --- feature players ----------------------------------------------------

    def _play_free_spins(
        self,
        game: GameExecutables,
        decks: ReelDecks,
        total: int,
        *,
        boosted_multiplier: int | None = None,
    ) -> None:
        game.start_free_spins(total)
        if boosted_multiplier is not None:
            while game.state.multiplier < boosted_multiplier:
                game.advance_multiplier("win")
        current = 0
        while current < total:
            current += 1
            game.free_spin(current, total)
            game.reveal(decks.draw("FR0"))
            self._play_cascades(game, decks, in_free_spins=True)
            scatters = count_symbols(game.state.board, SCATTER)
            if scatters >= 3 and min(scatters, 5) in SCATTER_RETRIGGER:
                total += SCATTER_RETRIGGER[min(scatters, 5)]

    def _play_hold_spin(self, game: GameExecutables, decks: ReelDecks, *, initial: bool) -> None:
        locked = self._initial_prizes() if initial else []
        game.start_hold_spin(locked, respins=HOLD_SPIN_RESPINS)
        while game.state.respins > 0 and len(game.state.locked) < FULL_LOCK:
            game.use_respin()
            new_locks = self._draw_with_locks(decks, set(game.state.locked))
            if new_locks:
                game.lock_hold_symbols(new_locks, reset_respins=HOLD_SPIN_RESET)
        total = sum(item["value"] for item in game.state.locked.values())
        game.end_hold_spin(total)

    def _initial_prizes(self) -> list[dict]:
        positions = self.rng.sample(range(FULL_LOCK), min(HOLD_SPIN_TRIGGER + 1, FULL_LOCK))
        return [
            {"reel": position // BOARD_ROWS, "row": position % BOARD_ROWS, "value": _random_prize_value(self.rng)}
            for position in positions
        ]

    def _draw_with_locks(self, decks: ReelDecks, locked: set[tuple[int, int]]) -> list[dict]:
        """Redraw unlocked cells from the Hold reel; return newly landed prizes."""
        board = decks.draw("HR0")
        new_locks: list[dict] = []
        for reel in range(BOARD_REELS):
            for row in range(BOARD_ROWS):
                if (reel, row) in locked:
                    continue
                if board[reel][row]["name"] == PRIZE:
                    new_locks.append({"reel": reel, "row": row, "value": _random_prize_value(self.rng)})
        return new_locks