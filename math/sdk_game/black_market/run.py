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
import sys
from pathlib import Path

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


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


def _approved_inputs_directory() -> Path:
    override = os.environ.get("BLM_APPROVED_INPUTS")
    if override:
        return Path(override).resolve()
    for candidate in (Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents):
        approved_inputs = candidate / "approved-inputs"
        if approved_inputs.is_dir():
            return approved_inputs
    return Path.cwd() / "approved-inputs"


def _require_production_approval() -> dict:
    approved_inputs = _approved_inputs_directory()
    tools_directory = approved_inputs.parent / "tools"
    if str(tools_directory) not in sys.path:
        sys.path.insert(0, str(tools_directory))
    try:
        from validate_approved_inputs import ApprovalValidationError, validate_input_directory

        return validate_input_directory(approved_inputs)
    except (ImportError, ApprovalValidationError) as exc:
        raise RuntimeError(
            "BLM_PRODUCTION=1 requires a validated non-provisional approval manifest in "
            f"{approved_inputs}: {exc}"
        ) from exc


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

    production = _env_flag("BLM_PRODUCTION")
    if production:
        _require_production_approval()

    run_conditions = {
        "run_sims": True,
        "run_optimization": _env_flag("BLM_RUN_OPTIMIZATION"),
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = ["base", "backroom", "vault", "black_card"]

    config = GameConfig()
    if production and config.provisional:
        raise RuntimeError("BLM_PRODUCTION=1 refuses a GameConfig marked provisional")
    if run_conditions["run_optimization"] and config.provisional:
        raise RuntimeError("BLM_RUN_OPTIMIZATION=1 refuses provisional optimization inputs")
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
