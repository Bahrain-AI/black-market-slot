"""BLACK MARKET state overrides — resets, criteria acceptance and prize symbols.

The SDK-conformant separation (matching ``0_0_cluster``) keeps per-round state
lifecycle and criteria acceptance rules in this layer, so the run flow in
``gamestate.py`` stays generic and auditable.
"""

import random

import game_events as events
from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """GameState lifecycle overrides for BLACK MARKET."""

    def reset_book(self) -> None:
        """Reset a fresh betting round (board + per-round counters)."""
        super().reset_book()
        self.cascade_number = 0
        self.expanded_reels = set()
        self.fs_mult_advanced = False
        self.hold_locked = {}
        self.respins = 0
        self.hold_prize_total = 0.0

    def reset_fs_spin(self) -> None:
        """Enter free-game mode and reset the multiplier progression."""
        super().reset_fs_spin()
        self.global_multiplier = self.config.multiplier_progression[0]
        self.fs_mult_advanced = False
        self.expanded_reels = set()

    def assign_special_sym_function(self) -> None:
        """Attach the prize-value draw to every created ``P`` (Hold & Spin) symbol."""
        self.special_symbol_functions = {"P": [self.assign_prize_value]}

    def assign_prize_value(self, sym) -> None:
        """Draw a prize value for a Hold & Spin coin (provisional prize pool)."""
        sym.prize = get_random_outcome(self.config.prize_pool)

    def _draw_hold_intro(self) -> None:
        """Fresh Hold & Spin starting board drawn from the HR0 deck (hybrid intro)."""
        self.refresh_special_syms()
        self.reelstrip_id = "HR0"
        self.reelstrip = self.config.reels["HR0"]
        board = [[None] * self.config.num_rows[r] for r in range(self.config.num_reels)]
        reel_positions = [
            random.randrange(0, len(self.reelstrip[reel])) for reel in range(self.config.num_reels)
        ]
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                name = self.reelstrip[reel][(reel_positions[reel] + row) % len(self.reelstrip[reel])]
                board[reel][row] = self.create_symbol(name)
        self.board = board
        self.reel_positions = reel_positions
        self.padding_position = [0] * self.config.num_reels
        self.anticipation = [0] * self.config.num_reels
        self.get_special_symbols_on_board()
        events.reveal(self)

    def check_repeat(self) -> None:
        """Reject the round unless its criteria constraints are satisfied."""
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            # Exact-win criteria (wincap -> MAX_WIN, "0" -> no win).
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
            # Display/force criteria must have actually triggered freespins.
            if self.get_current_distribution_conditions()["force_freegame"] and not (
                self.triggered_freegame
            ):
                self.repeat = True
            # Baseground/feature criteria cannot be won with a zero total win.
            if self.win_manager.running_bet_win == 0 and self.criteria != "0":
                self.repeat = True
        self.repeat_count += 1
        self.check_current_repeat_count()

    # --- Hold & Spin mechanics (buy modes: vault, black_card) ------------------
    def _initial_hold_locks(self) -> tuple:
        """Lock the prize positions already on the board (natural/first reveal)."""
        locked = []
        total = 0.0
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                sym = self.board[reel][row]
                if sym.name == "P":
                    value = float(getattr(sym, "prize", 0) or 0)
                    if value > 0:
                        locked.append({"reel": reel, "row": row, "value": int(round(value * 100, 0))})
                        sym.locked = True
                        total += value
        return locked, total

    def _draw_hold_respin(self) -> list:
        """One Hold & Spin respin: refill all unlocked cells from the HR0 deck.

        Returns the newly appearing prize positions, which are locked at once
        and emit a ``holdSpinLock`` (respins reset) in the calling flow.
        """
        hr = self.config.reels["HR0"]
        prizes = []
        for reel in range(self.config.num_reels):
            stop = random.randrange(0, len(hr[reel]))
            for row in range(self.config.num_rows[reel]):
                if (reel, row) in self.hold_locked:
                    continue
                sym = self.create_symbol(hr[reel][(stop + row) % len(hr[reel])])
                self.board[reel][row] = sym
                if sym.name == "P":
                    prizes.append(
                        {
                            "reel": reel,
                            "row": row,
                            "value": int(round(float(getattr(sym, "prize", 0) or 0) * 100, 0)),
                        }
                    )
                    sym.locked = True
        unlocked = [
            {"reel": r, "row": row}
            for r in range(self.config.num_reels)
            for row in range(self.config.num_rows[r])
            if (r, row) not in self.hold_locked
        ]
        events.refill(self, events.board_json(self.board), unlocked)
        return prizes