from copy import deepcopy

from . import game_events as events
from .game_calculations import expand_wild, next_multiplier, remove_and_collapse
from .gamestate import GameState


class GameExecutables:
    def __init__(self, state: GameState): self.state = state

    def reveal(self, board: list[list[dict]]) -> None:
        self.state.board = deepcopy(board)
        self.state.emit(events.reveal(self.state.board))

    def cascade(self, positions: list[dict], refill_symbols: list[list[dict]], amount: float, symbol: str, number: int) -> None:
        self.state.total_win = min(self.state.config.max_win, self.state.total_win + amount * self.state.multiplier)
        self.state.emit(events.win(positions, amount * self.state.multiplier, symbol))
        self.state.emit(events.cascade(number))
        self.state.emit(events.remove_symbols(positions))
        collapsed, refilled, refill_positions = remove_and_collapse(self.state.board, positions, refill_symbols)
        self.state.emit(events.collapse(collapsed))
        self.state.board = refilled
        self.state.emit(events.refill(refilled, refill_positions))

    def expanding_wild(self, reel: int) -> None:
        self.state.board, rows = expand_wild(self.state.board, reel)
        self.state.emit(events.expanding_wild(reel, rows))

    def start_free_spins(self, total: int) -> None:
        self.state.multiplier = self.state.config.multiplier_progression[0]
        self.state.emit(events.free_spins_start(total, self.state.multiplier))

    def free_spin(self, current: int, total: int) -> None:
        self.state.emit(events.free_spin(current, total, max(0, total - current)))

    def advance_multiplier(self, reason: str) -> None:
        before = self.state.multiplier
        self.state.multiplier = next_multiplier(before, self.state.config.multiplier_progression)
        if self.state.multiplier != before: self.state.emit(events.multiplier_increase(before, self.state.multiplier, reason))

    def start_hold_spin(self, locked: list[dict], respins: int = 3) -> None:
        self.state.respins = respins
        for item in locked: self.state.locked[(item["reel"], item["row"])] = deepcopy(item)
        self.state.emit(events.hold_spin_start(respins, list(self.state.locked.values())))

    def lock_hold_symbols(self, locks: list[dict], reset_respins: int = 3) -> None:
        for item in locks: self.state.locked[(item["reel"], item["row"])] = deepcopy(item)
        self.state.respins = reset_respins
        self.state.emit(events.hold_spin_lock(locks, reset_respins))

    def use_respin(self) -> None:
        self.state.respins = max(0, self.state.respins - 1)
        self.state.emit(events.hold_spin_respins(self.state.respins))

    def end_hold_spin(self, total: float) -> None:
        self.state.total_win = min(self.state.config.max_win, self.state.total_win + total)
        self.state.emit(events.hold_spin_end(total))

    def end_round(self) -> None:
        self.state.emit(events.payout(self.state.total_win, self.state.total_win))
        self.state.emit(events.round_end(self.state.total_win))
