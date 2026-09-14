"""Build a PROVISIONAL Stake Engine publication package for BLACK MARKET.

This tool exercises the exact publication pipeline required by the Engine
(index.json, per-mode JSONL books, LUTs, Zstandard compression, cross-file
validation, determination of the reported structure, replay records) with the
seeded provisional simulator.

OUTPUT IS DEVELOPMENT-ONLY: every generated artifact is marked provisional and
must be replaced by certified simulation output before any official submission.
No value here is approved production math.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

MATH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MATH_ROOT))

from black_market.game_config import GameConfig
from black_market.output import (
    compress_jsonl,
    validate_artifacts,
    write_index,
    write_uncompressed_mode,
)
from black_market.simulator import Simulator

PROVISIONAL_PACKAGE = "PROVISIONAL — development output, not approved production math"
REPLAY_KINDS = ("loss", "low_win", "mid_win", "high_win", "max_win")


def _stats(books: list[dict], cost: float) -> dict:
    payouts = [book["payoutMultiplier"] for book in books]
    wins = [payout for payout in payouts if payout > 0]
    count = len(payouts)
    return {
        "books": count,
        "hitRate": len(wins) / count,
        "lossPct": (count - len(wins)) / count,
        "provisionalWeightedRtp": sum(payouts) / (count * 100 * cost),
        "meanWin": (statistics.mean(wins) / 100) if wins else 0.0,
        "coefficientOfVariation": (statistics.pstdev(wins) / statistics.mean(wins)) if wins else 0.0,
        "payoutGe5x": sum(1 for payout in payouts if payout >= 500) / count,
        "payoutGe25x": sum(1 for payout in payouts if payout >= 2500) / count,
        "payoutGe100x": sum(1 for payout in payouts if payout >= 10000) / count,
        "maxWinCount": sum(1 for payout in payouts if payout >= 500000),
    }


def _replay_records(books: list[dict]) -> dict[str, dict]:
    records: dict[str, dict] = {}
    zero = [book for book in books if book["payoutMultiplier"] == 0]
    positive = sorted((book for book in books if book["payoutMultiplier"] > 0), key=lambda b: b["payoutMultiplier"])
    top = positive[-1] if positive else None
    if zero:
        records["loss"] = {"id": zero[0]["id"], "payoutMultiplier": 0}
    if top:
        records["max_win"] = {"id": top["id"], "payoutMultiplier": top["payoutMultiplier"]}
    bands = (
        ("low_win", lambda p: 0 < p < 500),
        ("mid_win", lambda p: 500 <= p < 2500),
        ("high_win", lambda p: 2500 <= p < 500000),
    )
    for name, match in bands:
        eligible = [book for book in positive if match(book["payoutMultiplier"])]
        if eligible:
            chosen = eligible[len(eligible) // 2]
            records[name] = {"id": chosen["id"], "payoutMultiplier": chosen["payoutMultiplier"]}
    return {"kinds": REPLAY_KINDS, "records": records}


def build_package(
    *,
    rounds_per_mode: int,
    seed: int,
    output: Path,
    overlay_reels: Path,
) -> dict:
    if rounds_per_mode <= 0:
        raise ValueError("rounds_per_mode must be positive")
    config = GameConfig()
    output.mkdir(parents=True, exist_ok=True)
    modes_report = []
    index_modes: list[dict] = []
    replay_manifest: dict[str, object] = {}

    for mode in config.bet_modes:
        if mode.name in replay_manifest:
            raise ValueError(f"duplicate mode {mode.name}")
        books = list(Simulator(config, mode.name, overlay_reels, seed=seed).rounds(rounds_per_mode))
        weights = {book["id"]: 1 for book in books}
        mode_entry = write_uncompressed_mode(output, mode, books, weights)
        source = output / mode_entry["events"]
        compressed = source.with_suffix(source.suffix + ".zst")
        compress_jsonl(source, compressed)
        source.unlink()
        mode_entry["events"] = compressed.name
        index_modes.append(mode_entry)
        modes_report.append({"name": mode.name, "cost": mode.cost, **mode_entry, **_stats(books, mode.cost)})
        replay_manifest[mode.name] = _replay_records(books)
        print(f"  {mode.name:<11} hitRate={modes_report[-1]['hitRate']:.4f} "
              f"rtp={modes_report[-1]['provisionalWeightedRtp']:.4f} "
              f"books={len(books)}", flush=True)

    write_index(output, index_modes)
    validation = validate_artifacts(output)

    package = {
        "status": PROVISIONAL_PACKAGE,
        "gameId": config.game_id,
        "board": {"reels": config.columns, "rows": config.rows},
        "targetRtp": config.target_rtp,
        "maxWin": config.max_win,
        "multiplierProgression": list(config.multiplier_progression),
        "roundsPerMode": rounds_per_mode,
        "seed": seed,
        "modes": modes_report,
        "validation": validation,
        "replayManifest": replay_manifest,
    }
    (output / "provisional-summary.json").write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    return package


def _default_reels() -> Path:
    return MATH_ROOT / "sdk_game" / "black_market" / "reels"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=100_000, help="rounds per mode (default 100k)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=MATH_ROOT / ".artifacts" / "provisional-package")
    parser.add_argument("--reels", type=Path, default=_default_reels())
    args = parser.parse_args()
    print("BLACK MARKET provisional package build")
    print("NOTE:", PROVISIONAL_PACKAGE)
    summary = build_package(
        rounds_per_mode=args.rounds,
        seed=args.seed,
        output=args.output,
        overlay_reels=args.reels,
    )
    output_path = (args.output / "provisional-summary.json").resolve()
    print(f"\nSummary written to: {output_path}")
    print(f"Total books: {sum(mode['books'] for mode in summary['modes'])}")