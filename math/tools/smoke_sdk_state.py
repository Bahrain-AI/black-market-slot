"""Stage and run the state-level smoke over the SDK-native BLACK MARKET game."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

MATH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MATH_ROOT))

from black_market.sdk import stage_sdk_game

PROGRAM = Path(__file__).with_name("sdk_state_program.py")


def smoke(sdk_root: Path) -> dict[str, object]:
    staged = stage_sdk_game(sdk_root)
    game_root = Path(staged["target"])
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(game_root), str(sdk_root.resolve()), str(MATH_ROOT)]
    )
    result = subprocess.run(
        [sys.executable, str(PROGRAM)],
        cwd=game_root,
        env=environment,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(result.returncode)
    report = json.loads(result.stdout)
    report["gameDir"] = str(game_root)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "sdk_root",
        nargs="?",
        type=Path,
        default=MATH_ROOT / ".stake-engine" / "math-sdk",
    )
    args = parser.parse_args()
    print(json.dumps(smoke(args.sdk_root), indent=2))