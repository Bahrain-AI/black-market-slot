"""Validate an existing Stake Engine delivery package for BLACK MARKET.

Cross-checks every book/LUT pay offset against its compressed result, and every
mode entry in ``index.json`` against its event and weight files, using the same
checks exercised by the automated tests.

Usage: python math/tools/validate_delivery.py --package <path>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MATH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MATH_ROOT))

from black_market.output import validate_artifacts


class ReleaseEligibilityError(ValueError):
    """Raised when a delivery package still contains provisional material."""


def _contains_provisional(value: object) -> bool:
    if isinstance(value, dict):
        return any(
            (key.lower() == "provisional" and item is not False)
            or _contains_provisional(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_provisional(item) for item in value)
    return isinstance(value, str) and "provisional" in value.lower()


def assert_release_eligible(package: Path) -> None:
    """Refuse any package marked provisional before release validation."""
    if not package.is_dir():
        raise ReleaseEligibilityError(f"release package is missing: {package}")
    named_markers = sorted(path.name for path in package.rglob("*provisional*"))
    if named_markers:
        raise ReleaseEligibilityError(f"release package contains provisional artifact(s): {', '.join(named_markers)}")
    for path in sorted(package.rglob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ReleaseEligibilityError(f"release package has invalid JSON: {path.name}") from exc
        if _contains_provisional(value):
            raise ReleaseEligibilityError(f"release package JSON is marked provisional: {path.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True, help="directory containing index.json, books, and LUTs")
    args = parser.parse_args()

    if not (args.package / "index.json").is_file():
        print(f"error: no index.json found in {args.package}")
        return 2

    try:
        assert_release_eligible(args.package)
        report = validate_artifacts(args.package)
    except (ReleaseEligibilityError, ValueError) as exc:
        print(f"error: {exc}")
        return 1
    modes = report.get("modes", report)
    mode_count = len(modes) if isinstance(modes, (list, dict)) else 0
    print(json.dumps(report, indent=2))
    print(f"validated package: {args.package} ({mode_count} modes)")
    return 0 if report.get("valid", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
