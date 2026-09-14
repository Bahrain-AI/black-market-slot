import csv
import json
from pathlib import Path
from typing import Iterable

from .game_config import BetMode


def validate_book(book: dict) -> None:
    if not {"id", "events", "payoutMultiplier"}.issubset(book): raise ValueError("book requires id, events and payoutMultiplier")
    for index, event in enumerate(book["events"]):
        if event.get("index") != index or not event.get("type"): raise ValueError(f"invalid event at index {index}")


def write_uncompressed_mode(output: Path, mode: BetMode, books: Iterable[dict], weights: dict[int, int]) -> dict:
    """Write validated provisional output; compression remains a separate SDK hook."""
    materialized = list(books)
    if not materialized: raise ValueError("refusing to fabricate an empty production book")
    output.mkdir(parents=True, exist_ok=True)
    book_name = f"books_{mode.name}.jsonl"
    lookup_name = f"lookUpTable_{mode.name}_0.csv"
    with (output / book_name).open("w", encoding="utf-8") as handle:
        for book in materialized:
            validate_book(book)
            handle.write(json.dumps(book, separators=(",", ":")) + "\n")
    with (output / lookup_name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        for book in materialized: writer.writerow([book["id"], weights.get(book["id"], 1), book["payoutMultiplier"]])
    return {"name": mode.name, "cost": mode.cost, "events": book_name, "weights": lookup_name}


def write_index(output: Path, modes: list[dict]) -> None:
    if not modes: raise ValueError("index requires at least one generated mode")
    (output / "index.json").write_text(json.dumps({"modes": modes}, indent=2) + "\n", encoding="utf-8")


def compress_jsonl(source: Path, destination: Path) -> None:
    try: import zstandard
    except ImportError as exc: raise RuntimeError("Install the official Math SDK dependencies, including zstandard, before compression") from exc
    compressor = zstandard.ZstdCompressor(level=10)
    with source.open("rb") as reader, destination.open("wb") as writer: compressor.copy_stream(reader, writer)
