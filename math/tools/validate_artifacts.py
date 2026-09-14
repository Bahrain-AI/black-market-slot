"""Validate local Stake Engine math artifacts without uploading them."""

import argparse
import json
from pathlib import Path
import sys

MATH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MATH_ROOT))

from black_market.output import validate_artifacts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing index.json")
    args = parser.parse_args()
    print(json.dumps(validate_artifacts(args.directory), indent=2))
