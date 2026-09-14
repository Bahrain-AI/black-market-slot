"""Main file for generating results for BLACK MARKET (SDK-native pipeline).

Run from the SDK root::

    python games/black_market/run.py

Simulation sizes can be overridden via environment variables so quick smoke
runs and the full provisioning runs share one entry point::

    BLM_BASE_SIMS=2000 BLM_BACKROOM_SIMS=1000 BLM_VAULT_SIMS=1000 \\
    BLM_BLACK_CARD_SIMS=1000 python games/black_market/run.py

Optimisation (the Windows-free Rust step) is intentionally disabled by default
here; the sanctioned optimizer round runs separately once approved math inputs
are supplied.
"""

import os

from game_config import GameConfig
from game_optimization import OptimizationSetup
from gamestate import GameState
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    return int(raw) if raw else default


def _remove_stale_optimized_luts(config) -> None:
    """Remove previously published ``lookUpTable_<mode>_0.csv`` copies.

    The SDK only re-creates the "_0" LUT from the freshly simulated linear lookup
    table when that file does *not* already exist
    (``src/write_data/write_data.py``: ``output_lookup_and_force_files``). In the
    unoptimized pipeline the "_0" file is a plain copy of that run's lookup table,
    so a leftover copy from an earlier run at a different simulation scale would
    publish LUT ids that no longer match the fresh books — breaking the analysis
    step (``weights[idx - 1]``) and the delivered ``index.json``.
    """
    from src.config.paths import PATH_TO_GAMES

    publish_dir = os.path.join(PATH_TO_GAMES, config.game_id, "library", "publish_files")
    for name in sorted(os.listdir(publish_dir)):
        if name.startswith("lookUpTable") and name.endswith("_0.csv"):
            stale = os.path.join(publish_dir, name)
            print(f"Removing stale publish LUT: {stale}")
            os.remove(stale)


if __name__ == "__main__":

    num_threads = 10
    rust_threads = 20
    batching_size = 50000
    compression = True
    profiling = False

    num_sim_args = {
        "base": _env_int("BLM_BASE_SIMS", 25_000),
        "backroom": _env_int("BLM_BACKROOM_SIMS", 10_000),
        "vault": _env_int("BLM_VAULT_SIMS", 10_000),
        "black_card": _env_int("BLM_BLACK_CARD_SIMS", 10_000),
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": False,  # Rust optimizer binary not available in this environment.
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = ["base", "backroom", "vault", "black_card"]

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        OptimizationSetup(config)

    if run_conditions["run_sims"]:
        _remove_stale_optimized_luts(config)
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        from optimization_program.run_script import OptimizationExecution

        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)