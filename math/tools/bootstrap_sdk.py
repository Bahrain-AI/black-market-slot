"""Create or verify the pinned official Stake Engine Math SDK checkout."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

MATH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MATH_ROOT))

from black_market.sdk import SDK_COMMIT, SDK_REPOSITORY, stage_sdk_game, validate_sdk_checkout


def run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def bootstrap(destination: Path) -> dict[str, object]:
    destination = destination.resolve()
    if destination.exists():
        report = validate_sdk_checkout(destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--filter=blob:none", "--no-checkout", SDK_REPOSITORY, str(destination)])
        run(["git", "checkout", SDK_COMMIT], cwd=destination)
        report = validate_sdk_checkout(destination)
    report["game"] = stage_sdk_game(destination)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination",
        nargs="?",
        type=Path,
        default=MATH_ROOT / ".stake-engine" / "math-sdk",
    )
    args = parser.parse_args()
    print(json.dumps(bootstrap(args.destination), indent=2))
