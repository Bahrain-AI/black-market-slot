"""Record replay book IDs (loss / low / mid / high / max) from SDK books.

The Engine staging flow needs ``replay=true&event=<mode>/<id>`` to render a loss,
a normal win, a big win and a max win for *every* mode. This tool scans the
generated SDK books (``publish_files/books_<mode>.jsonl.zst``), buckets each
book by payout using the same bands as the provisional package builder, and
writes a ``replay_manifest.json`` next to the published package.

Provisional note: the manifest references the *current* pipeline books. Once the
approved production inputs replace the provisional ones and the full certified
simulation set runs, re-run this tool so the recorded IDs point at the shipped
books.

Usage: python math/tools/find_sdk_replays.py [publish_files_dir]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MATH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MATH_ROOT))

from black_market.output import _book_stream

REPLAY_KINDS = ("loss", "low_win", "mid_win", "high_win", "max_win")

# Band thresholds in payout hundredths (book "payoutMultiplier").
LOW_MIN, LOW_MAX = 1, 500          # 0.01x .. <5x
MID_MIN, MID_MAX = 500, 2500       # 5x .. <25x
HIGH_MIN, HIGH_MAX = 2500, 500000  # 25x .. <5000x (max win cap = 500_000)


def _records_for_book(payout: int) -> str | None:
    if payout <= 0:
        return "loss"
    if payout < LOW_MAX:
        return "low_win"
    if payout < MID_MAX:
        return "mid_win"
    if payout < HIGH_MAX:
        return "high_win"
    return "max_win"


def find_replays(publish_files: Path) -> dict[str, object]:
    mode_files = sorted(publish_files.glob("books_*.jsonl.zst"))
    if not mode_files:
        raise ValueError(f"no books_*.jsonl.zst in {publish_files}")

    manifest: dict[str, object] = {
        "source": str(publish_files.resolve()),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "provisional": True,
        "note": "IDs reference the current provisional pipeline books; regenerate after the approved production simulation set.",
        "modes": {},
    }
    for path in mode_files:
        mode = path.name.removeprefix("books_").removesuffix(".jsonl.zst")
        buckets: dict[str, list[dict]] = {kind: [] for kind in REPLAY_KINDS}
        book_count = 0
        with _book_stream(path) as handle:
            for line in handle:
                if not line.strip():
                    continue
                book = json.loads(line)
                book_count += 1
                kind = _records_for_book(book["payoutMultiplier"])
                buckets[kind].append(
                    {"id": book["id"], "payoutMultiplier": book["payoutMultiplier"]}
                )
        records: dict[str, dict] = {}
        for kind in REPLAY_KINDS:
            if not buckets[kind]:
                continue
            if kind == "max_win":
                chosen = max(buckets[kind], key=lambda r: r["payoutMultiplier"])
            else:
                chosen = buckets[kind][len(buckets[kind]) // 2]
            records[kind] = chosen
        manifest["modes"][mode] = {
            "books": book_count,
            "kinds": REPLAY_KINDS,
            "records": records,
        }
        print(
            f"  {mode:<12} books={book_count:<6} "
            + ", ".join(f"{k}={rec['id']}({rec['payoutMultiplier']})" for k, rec in records.items())
        )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "publish_files",
        nargs="?",
        type=Path,
        default=(MATH_ROOT / ".stake-engine" / "math-sdk" / "games" / "black_market" / "library" / "publish_files"),
    )
    args = parser.parse_args()
    publish_files = args.publish_files.resolve()
    if not publish_files.is_dir():
        print(f"error: {publish_files} is not a directory")
        return 2

    manifest = find_replays(publish_files)
    output = publish_files / "replay_manifest.json"
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())