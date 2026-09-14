"""BLACK MARKET optimization setup (Provisional fences).

The RTP fences below are *provisional* placeholders matching the provisional
phase-1 inputs — they are deliberately NOT tuned to the real game yield, and
the sanctioned optimizer round (with approved paytable/reels) must replace
them.  Constraint kept strict: each mode's condition RTPs sum exactly to the
mode RTP so ``verify_optimization_input`` passes for the pipeline runs.
"""

from optimization_program.optimization_config import (
    ConstructConditions,
    ConstructFenceBias,
    ConstructParameters,
    ConstructScaling,
    verify_optimization_input,
)

TARGET_MODE_RTP = 0.96


class OptimizationSetup:
    """Amends game_config.opt_params (required for analysis/config generation)."""

    def __init__(self, game_config):
        self.game_config = game_config
        wincaps = {}
        for bm in game_config.bet_modes:
            wincaps[bm.get_name()] = bm.get_wincap()

        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.001, av_win=wincaps["base"], search_conditions=wincaps["base"]
                    ).return_dict(),
                    "freegame": ConstructConditions(rtp=0.76, hr=200, search_conditions={"symbol": "scatter"}).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "basegame": ConstructConditions(
                        rtp=0.199, hr=2, search_conditions={}
                    ).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {"criteria": "basegame", "scale_factor": 1.2, "win_range": (1, 2), "probability": 1.0},
                        {"criteria": "basegame", "scale_factor": 0.9, "win_range": (10, 25), "probability": 1.0},
                        {"criteria": "freegame", "scale_factor": 0.8, "win_range": (500, 1500), "probability": 1.0},
                        {"criteria": "freegame", "scale_factor": 1.3, "win_range": (3000, 4000), "probability": 1.0},
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(0.5, 1.5)],
                    bias_weights=[0.4],
                ).return_dict(),
            },
            "backroom": {
                "conditions": {
                    "freegame": ConstructConditions(
                        rtp=TARGET_MODE_RTP, hr=220, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {"criteria": "freegame", "scale_factor": 0.9, "win_range": (20, 50), "probability": 1.0},
                        {"criteria": "freegame", "scale_factor": 1.4, "win_range": (3000, 5000), "probability": 1.0},
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["freegame"],
                    bias_ranges=[(0.5, 1.5)],
                    bias_weights=[0.4],
                ).return_dict(),
            },
            "vault": {
                "conditions": {
                    "holdspin": ConstructConditions(
                        rtp=TARGET_MODE_RTP, hr=10, search_conditions={}
                    ).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {"criteria": "holdspin", "scale_factor": 1.1, "win_range": (5, 50), "probability": 1.0},
                        {"criteria": "holdspin", "scale_factor": 0.8, "win_range": (500, 2500), "probability": 1.0},
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["holdspin"],
                    bias_ranges=[(0.5, 1.5)],
                    bias_weights=[0.4],
                ).return_dict(),
            },
            "black_card": {
                "conditions": {
                    "hybrid": ConstructConditions(
                        rtp=TARGET_MODE_RTP, hr=120, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {"criteria": "hybrid", "scale_factor": 1.0, "win_range": (50, 150), "probability": 1.0},
                        {"criteria": "hybrid", "scale_factor": 0.85, "win_range": (2500, 5000), "probability": 1.0},
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["hybrid"],
                    bias_ranges=[(0.5, 1.5)],
                    bias_weights=[0.4],
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)