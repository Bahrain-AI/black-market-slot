"""BLACK MARKET cluster evaluation on top of the SDK cluster engine.

Pay-anywhere cluster wins use the pinned SDK ``Cluster`` flood-fill in exactly
the same way as the ``0_0_cluster`` sample game.  Expanding Wilds (W) fill
their full reel before each evaluation, then join (and explode with) every
cluster they touch via the SDK ``wild_key`` handling.
"""

import game_events as events
from src.calculations.cluster import Cluster
from src.executables.executables import Executables


class GameCalculations(Executables):
    """Game-specific evaluation logic (board + win analysis)."""

    def expand_wilds_on_board(self) -> None:
        """Expand every landed Wild into a full-reel Wild (once per draw)."""
        for reel in range(self.config.num_reels):
            names = [self.board[reel][row].name for row in range(self.config.num_rows[reel])]
            if "W" in names and not all(n == "W" for n in names):
                for row in range(self.config.num_rows[reel]):
                    self.board[reel][row] = self.create_symbol("W")
                events.expanding_wild(self, reel, list(range(self.config.num_rows[reel])))

    def get_clusters_update_wins(self) -> None:
        """Detect clusters (after wild expansion), record wins, flag explosive symbols."""
        self.expand_wilds_on_board()
        self.win_data = Cluster.get_cluster_data(
            self.config,
            self.board,
            self.global_multiplier,
            multiplier_key="multiplier",
            wild_key="wild",
        )
        if self.win_data["totalWin"] > 0:
            self.win_manager.update_spinwin(self.win_data["totalWin"])
            Cluster.record_cluster_wins(self)