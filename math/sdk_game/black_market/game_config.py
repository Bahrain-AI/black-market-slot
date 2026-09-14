"""Provisional BLACK MARKET configuration for the official Stake Engine Math SDK."""

import os

from src.config.betmode import BetMode
from src.config.config import Config
from src.config.distributions import Distribution

TARGET_RTP = 0.96
MAX_WIN = 5_000.0
MULTIPLIER_PROGRESSION = [1, 2, 3, 5, 10]


def _distribution(criteria, quota, reels, *, force_freegame=False, feature="base", win_criteria=None):
    return Distribution(
        criteria=criteria,
        quota=quota,
        win_criteria=win_criteria,
        conditions={
            "reel_weights": reels,
            "force_wincap": criteria == "wincap",
            "force_freegame": force_freegame,
            "feature": feature,
            "multiplier_progression": MULTIPLIER_PROGRESSION,
        },
    )


class GameConfig(Config):
    """SDK-native configuration; values remain provisional until optimization."""

    def __init__(self):
        super().__init__()
        self.game_id = "black_market"
        self.game_name = "black_market"
        self.working_name = "BLACK MARKET"
        self.provider_number = 0
        self.wincap = MAX_WIN
        self.win_type = "scatter"
        self.rtp = TARGET_RTP
        self.provisional = True
        self.construct_paths()

        self.num_reels = 5
        self.num_rows = [4] * self.num_reels
        self.multiplier_progression = MULTIPLIER_PROGRESSION.copy()
        self.paytable = self.convert_range_table(
            {
                ((8, 9), "H1"): 2.0,
                ((10, 11), "H1"): 5.0,
                ((12, 14), "H1"): 12.0,
                ((15, 20), "H1"): 35.0,
                ((8, 9), "H2"): 1.5,
                ((10, 11), "H2"): 4.0,
                ((12, 14), "H2"): 9.0,
                ((15, 20), "H2"): 25.0,
                ((8, 9), "H3"): 1.0,
                ((10, 11), "H3"): 3.0,
                ((12, 14), "H3"): 7.0,
                ((15, 20), "H3"): 18.0,
                ((8, 9), "H4"): 0.8,
                ((10, 11), "H4"): 2.0,
                ((12, 14), "H4"): 5.0,
                ((15, 20), "H4"): 14.0,
                ((8, 9), "L1"): 0.5,
                ((10, 11), "L1"): 1.2,
                ((12, 14), "L1"): 3.0,
                ((15, 20), "L1"): 8.0,
                ((8, 9), "L2"): 0.4,
                ((10, 11), "L2"): 1.0,
                ((12, 14), "L2"): 2.5,
                ((15, 20), "L2"): 6.0,
                ((8, 9), "L3"): 0.3,
                ((10, 11), "L3"): 0.8,
                ((12, 14), "L3"): 2.0,
                ((15, 20), "L3"): 5.0,
                ((8, 9), "L4"): 0.2,
                ((10, 11), "L4"): 0.6,
                ((12, 14), "L4"): 1.5,
                ((15, 20), "L4"): 4.0,
            }
        )
        self.include_padding = True
        self.special_symbols = {"wild": ["W"], "scatter": ["S"], "prize": ["P"]}
        self.freespin_triggers = {
            self.basegame_type: {3: 8, 4: 10, 5: 12},
            self.freegame_type: {3: 3, 4: 5, 5: 8},
        }
        self.anticipation_triggers = {self.basegame_type: 2, self.freegame_type: 2}

        reel_files = {"BR0": "BR0.csv", "FR0": "FR0.csv", "HR0": "HR0.csv"}
        self.reels = {
            name: self.read_reels_csv(os.path.join(self.reels_path, filename))
            for name, filename in reel_files.items()
        }
        self.padding_reels = {
            self.basegame_type: self.reels["BR0"],
            self.freegame_type: self.reels["FR0"],
        }

        base_reels = {self.basegame_type: {"BR0": 1}, self.freegame_type: {"FR0": 1}}
        feature_reels = {self.basegame_type: {"BR0": 1}, self.freegame_type: {"FR0": 1}}
        hold_reels = {self.basegame_type: {"HR0": 1}}
        self.bet_modes = [
            BetMode(
                name="base", cost=1.0, rtp=self.rtp, max_win=self.wincap,
                auto_close_disabled=False, is_feature=True, is_buybonus=False,
                distributions=[
                    _distribution("wincap", 0.001, base_reels, force_freegame=True, win_criteria=self.wincap),
                    _distribution("freegame", 0.099, feature_reels, force_freegame=True, feature="free_spins"),
                    _distribution("0", 0.4, {self.basegame_type: {"BR0": 1}}),
                    _distribution("basegame", 0.5, {self.basegame_type: {"BR0": 1}}),
                ],
            ),
            BetMode(
                name="backroom", cost=60.0, rtp=self.rtp, max_win=self.wincap,
                auto_close_disabled=False, is_feature=False, is_buybonus=True,
                distributions=[_distribution("freegame", 1.0, feature_reels, force_freegame=True, feature="free_spins")],
            ),
            BetMode(
                name="vault", cost=100.0, rtp=self.rtp, max_win=self.wincap,
                auto_close_disabled=False, is_feature=False, is_buybonus=True,
                distributions=[_distribution("holdspin", 1.0, hold_reels, feature="hold_spin")],
            ),
            BetMode(
                name="black_card", cost=200.0, rtp=self.rtp, max_win=self.wincap,
                auto_close_disabled=False, is_feature=False, is_buybonus=True,
                distributions=[_distribution("hybrid", 1.0, feature_reels, force_freegame=True, feature="hybrid")],
            ),
        ]
