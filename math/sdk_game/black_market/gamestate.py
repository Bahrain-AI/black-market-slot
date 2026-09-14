"""BLACK MARKET gamestate — the SDK-native spin/freespin/hold&spin flow.

Mirrors the ``0_0_cluster`` sample flow (draw -> cluster wins -> tumble until
empty/wincap), extended with:
  * expanding Wilds and prize ``P`` symbols,
  * freespin multiplier progression [1, 2, 3, 5, 10],
  * Hold & Spin bonus rounds (vault / black_card buy modes),
  * event emission restricted to the frontend contract (see ``game_events.py``).
"""

import game_events as events
from game_override import GameStateOverride


class GameState(GameStateOverride):
    """SDK-native BLACK MARKET game state."""

    def __init__(self, config):
        super().__init__(config)

    # --- base game --------------------------------------------------------------
    def run_spin(self, sim, simulation_seed=None):
        """Run a single bet round, re-drawing until the criteria constraints pass."""
        self.reset_seed(sim, simulation_seed)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()
            self.get_clusters_update_wins()
            self.emit_tumble_win_events()
            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            # Buy-mode bonus: Vault = forced Hold & Spin, Black Card =
            # forced free-spins (above) followed by a forced Hold & Spin.
            if self.criteria in ("holdspin", "hybrid"):
                self.run_holdspin()

            self.evaluate_finalwin()
            self.check_repeat()
        self.imprint_wins()

    # --- free spins -------------------------------------------------------------
    def run_freespin(self):
        """Run the awarded free-spins with multiplier progression and retriggers."""
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()
            self.get_clusters_update_wins()
            self.emit_tumble_win_events()
            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()
        self.end_freespin()

    # --- hold & spin (bonus round) ----------------------------------------------
    def run_holdspin(self):
        """Hold & Spin: lock landed prizes; each respin refills unlocked cells
        and resets the respin counter on every new lock."""
        if self.criteria == "hybrid":
            # Black Card: the H&S phase opens with its own HR0 reveal so the
            # bonus starts from a real Hold & Spin board.
            self._draw_hold_intro()
        locked, total = self._initial_hold_locks()
        self.hold_locked = {(it["reel"], it["row"]): it for it in locked}
        self.hold_prize_total = total
        events.hold_spin_start(self, self.config.holdspin_respins, locked)
        self.respins = self.config.holdspin_respins
        full_board = self.config.num_reels * self.config.num_rows[0]

        while self.respins > 0 and len(self.hold_locked) < full_board and not self.wincap_triggered:
            self.respins -= 1
            events.hold_spin_respins(self, self.respins)
            prizes = self._draw_hold_respin()
            if prizes:
                for p in prizes:
                    self.hold_locked[(p["reel"], p["row"])] = p
                    self.hold_prize_total += p["value"] / 100.0
                self.respins = self.config.holdspin_respins
                events.hold_spin_lock(self, prizes, self.config.holdspin_respins)

        events.hold_spin_end(self, int(round(self.hold_prize_total * 100, 0)))
        # Flush the bonus prize total as a discrete win of the round (spin_win
        # still holds the previous phase's flush amount, so reset it first).
        self.win_manager.reset_spin_win()
        self.win_manager.update_spinwin(self.hold_prize_total)
        self.win_manager.update_gametype_wins(self.config.basegame_type)