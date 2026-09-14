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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True, help="directory containing index.json, books, and LUTs")
    args = parser.parse_args()

    if not (args.package / "index.json").is_file():
        print(f"error: no index.json found in {args.package}")
        return 2

    report = validate_artifacts(args.package)
    modes = report.get("modes", report)
    mode_count = len(modes) if isinstance(modes, (list, dict)) else 0
    print(json.dumps(report, indent=2))
    print(f"validated package: {args.package} ({mode_count} modes)")
    return 0 if report.get("valid", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())