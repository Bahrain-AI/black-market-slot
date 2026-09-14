"""BLACK MARKET game flow — the SDK side emits the frontend event contract.

Every method below overrides the equivalent SDK ``Executables``/``Board``
method (or mirrors its non-emission mechanics) so that a book only ever
contains the sixteen BLACK MARKET events defined in ``game_events.py``.
"""

import game_events as events
from game_calculations import GameCalculations
from src.calculations.statistics import get_random_outcome


class GameExecutables(GameCalculations):
    """Per-action flow: draws, tumble sequences, freespin and round end."""

    # --- board draw ------------------------------------------------------------
    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Draw/re-draw a board following the SDK criteria contract.

        ``force_freegame`` criteria guarantee an FS trigger by seeding the
        initial reveal with ``scatter_triggers`` scatters (same approach as the
        ``0_0_cluster`` sample).  `Non-forcing criteria re-draw while enough
        scatters would naturally trigger freespins, keeping the base/feature
        split criteria-driven (as the RGS force-lookup convention requires).
        """
        distribution_conditions = self.get_current_distribution_conditions()
        if distribution_conditions["force_freegame"] and self.gametype == self.config.basegame_type:
            num_scatters = get_random_outcome(distribution_conditions["scatter_triggers"])
            self.force_special_board(trigger_symbol, num_scatters)
        elif (
            not distribution_conditions["force_freegame"] and self.gametype == self.config.basegame_type
        ):
            self.create_board_reelstrips()
            while self.count_special_symbols(trigger_symbol) >= min(
                self.config.freespin_triggers[self.gametype].keys()
            ):
                self.create_board_reelstrips()
        else:
            self.create_board_reelstrips()
        self.expanded_reels = set()
        if emit_event:
            events.reveal(self)

    # --- win events / tumble ---------------------------------------------------
    def emit_tumble_win_events(self) -> None:
        """Transmit per-cluster win, cascade and removeSymbol events."""
        if self.win_data["totalWin"] > 0:
            for w in self.win_data["wins"]:
                events.win(self, w["positions"], int(round(w["win"] * 100, 0)), w["symbol"])
            self.cascade_number += 1
            events.cascade(self, self.cascade_number)
            positions = []
            for w in self.win_data["wins"]:
                for p in w["positions"]:
                    if p not in positions:
                        positions.append(p)
            events.remove_symbols(self, positions)
            # Free-spins multiplier progression: +1 step on the first winning
            # evaluation of each freespin (reason "win").
            if self.gametype == self.config.freegame_type and not self.fs_mult_advanced:
                self.update_global_mult()
                self.fs_mult_advanced = True
            self.evaluate_wincap()

    def _collapsed_board(self, positions) -> list:
        """Snapshot of the board immediately after symbol removal (empty-on-top)."""
        removed = {(p["reel"], p["row"]) for p in positions}
        board = []
        for reel in range(self.config.num_reels):
            survivors = [
                events.json_sym(self.board[reel][row])
                for row in range(self.config.num_rows[reel])
                if (reel, row) not in removed
            ]
            missing = self.config.num_rows[reel] - len(survivors)
            board.append([{"name": "empty"} for _ in range(missing)] + survivors)
        return board

    def tumble_game_board(self) -> None:
        """Remove exploding symbols (collapse) and refill from the active reelstrip."""
        positions = []
        for w in self.win_data["wins"]:
            for p in w["positions"]:
                if p not in positions:
                    positions.append(p)
        events.collapse(self, self._collapsed_board(positions))
        self.tumble_board()
        refill_positions = []
        for reel, newsyms in enumerate(self.new_symbols_from_tumble):
            if newsyms:
                refill_positions.extend({"reel": reel, "row": row} for row in range(len(newsyms)))
        events.refill(self, events.board_json(self.board), refill_positions)

    def set_end_tumble_event(self) -> None:
        """No end-of-tumble event in the BLACK MARKET contract."""

    def evaluate_wincap(self) -> bool:
        """Indicate the spin/freespin sequence should stop at max-win."""
        if self.win_manager.running_bet_win >= self.config.wincap and not (self.wincap_triggered):
            self.wincap_triggered = True
            return True
        return False

    # --- free spins ------------------------------------------------------------
    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Set initial free-spin count and transmit the FS start event."""
        self.tot_fs = self.config.freespin_triggers[self.gametype][self.count_special_symbols(scatter_key)]
        events.free_spins_start(self, self.tot_fs, self.global_multiplier)

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """On FS retrigger extend the spin count and re-send the start event."""
        self.tot_fs += self.config.freespin_triggers[self.gametype][self.count_special_symbols(scatter_key)]
        events.free_spins_start(self, self.tot_fs, self.global_multiplier)

    def update_freespin(self) -> None:
        """Advance to the next freespin (emitted as ``freeSpin``, before reveal)."""
        events.free_spin(self, self.fs + 1, self.tot_fs)
        self.fs += 1
        self.win_manager.reset_spin_win()
        self.win_data = {"totalWin": 0, "wins": []}
        self.fs_mult_advanced = False
        self.expanded_reels = set()

    def end_freespin(self) -> None:
        """No freeSpinEnd event in the BLACK MARKET contract."""

    def update_global_mult(self) -> None:
        """Advance the freespin multiplier along the configured progression."""
        progression = self.config.multiplier_progression
        try:
            idx = progression.index(self.global_multiplier)
        except ValueError:
            idx = 0
        if idx < len(progression) - 1:
            before = self.global_multiplier
            self.global_multiplier = progression[idx + 1]
            events.multiplier_increase(self, before, self.global_multiplier, "win")

    # --- round end -------------------------------------------------------------
    def evaluate_finalwin(self) -> None:
        """Finalize book payout multipliers and emit payout + roundEnd."""
        self.update_final_win()
        capped_total = min(self.win_manager.running_bet_win, self.config.wincap)
        events.payout(self, int(round(self.final_win * 100, 0)), int(round(capped_total * 100, 0)))
        events.round_end(self, int(round(self.final_win * 100, 0)))