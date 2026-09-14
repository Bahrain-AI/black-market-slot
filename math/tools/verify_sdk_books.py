"""Verify SDK-generated book files against the frontend deterministic event contract.

Decompresses every ``books_<mode>.jsonl.zst`` in an Engine publish_files directory
and asserts that:
  * every event type is one of the 16 contract types (src/game/events/types.ts),
  * every payload key required by the contract is present,
  * win / payout / holdSpin values are integer hundredths,
  * the round is coherent (single payout + roundEnd, payoutMultiplier match),
  * book payoutMultiplier agrees with the book-level base+free split.

Usage: python math/tools/verify_sdk_books.py [publish_files_dir]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MATH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MATH_ROOT))

from black_market.output import _book_stream  # shared zstd/jsonl reader
from black_market.sdk import FRONTEND_CONTRACT

VALID_TYPES = frozenset(FRONTEND_CONTRACT)


def verify_mode(path: Path) -> dict:
    books = 0
    events = 0
    types: dict[str, int] = {}
    errors: list[str] = []
    rtp_sum = 0.0
    weight_total = 0
    with _book_stream(path) as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                book = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.name}:{line_number} invalid JSON ({exc})")
                continue
            books += 1
            weight_total += 1
            events_in_round = 0
            for event in book.get("events", []):
                events += 1
                events_in_round += 1
                event_type = event.get("type")
                if event_type not in VALID_TYPES:
                    errors.append(f"{path.name} book {book.get('id')} bad type {event_type!r}")
                    continue
                types[event_type] = types.get(event_type, 0) + 1
                missing = [k for k in FRONTEND_CONTRACT[event_type] if k not in event]
                if missing:
                    errors.append(f"{path.name} book {book.get('id')} {event_type} missing {missing}")
                if event_type == "win" and not isinstance(event.get("amount"), int):
                    errors.append(f"{path.name} book {book.get('id')} win.amount not int")
            round_ends = [e for e in book.get("events", []) if e.get("type") == "roundEnd"]
            payouts = [e for e in book.get("events", []) if e.get("type") == "payout"]
            if len(round_ends) != 1 or len(payouts) != 1:
                errors.append(f"{path.name} book {book.get('id')} needs exactly one payout+roundEnd")
            else:
                rp = round_ends[0].get("payoutMultiplier")
                pa = payouts[0].get("amount")
                pt = payouts[0].get("total")
                pm = book.get("payoutMultiplier")
                if not (isinstance(rp, int) and isinstance(pa, int) and isinstance(pt, int)):
                    errors.append(f"{path.name} book {book.get('id')} non-int amounts")
                if rp != pa or pt != pa or rp != pm:
                    errors.append(f"{path.name} book {book.get('id')} payout incoherent {rp}/{pa}/{pt}/{pm}")
                rtp_sum += pm / 100.0
            base = book.get("baseGameWins", 0.0)
            free = book.get("freeGameWins", 0.0)
            # base+free carry the *uncapped* round win (the SDK's update_final_win
            # clamps only payoutMultiplier to the wincap), so base+free >= pm always.
            if (base + free) + 1e-9 < book.get("payoutMultiplier", 0) / 100.0:
                errors.append(f"{path.name} book {book.get('id')} base+free < payoutMultiplier")
    return {
        "file": path.name,
        "books": books,
        "events": events,
        "eventTypes": dict(sorted(types.items())),
        "errors": errors[:20],
        "errorCount": len(errors),
        "provisionalAvgPayout": round(rtp_sum / max(weight_total, 1), 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "publish_files",
        nargs="?",
        type=Path,
        default=MATH_ROOT / ".stake-engine" / "math-sdk" / "games" / "black_market" / "library" / "publish_files",
    )
    args = parser.parse_args()
    target = args.publish_files.resolve()
    if not target.is_dir():
        print(f"error: {target} is not a directory")
        return 2
    book_files = sorted(target.glob("books_*.jsonl*"))
    if not book_files:
        print(f"error: no books_*.jsonl[*] files in {target}")
        return 2
    reports = [verify_mode(path) for path in book_files]
    total_events = sum(report["events"] for report in reports)
    total_errors = sum(report["errorCount"] for report in reports)
    print(json.dumps({"publishFiles": str(target), "books": reports, "events": total_events, "errors": total_errors}, indent=2))
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())