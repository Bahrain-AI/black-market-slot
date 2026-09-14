import csv
import io
import json
from pathlib import Path
from typing import Iterable, TextIO

from .game_config import BetMode


def validate_book(book: dict) -> None:
    if not {"id", "events", "payoutMultiplier"}.issubset(book):
        raise ValueError("book requires id, events and payoutMultiplier")
    if not isinstance(book["id"], int) or book["id"] < 0:
        raise ValueError("book id must be an unsigned integer")
    payout = book["payoutMultiplier"]
    if not isinstance(payout, int) or isinstance(payout, bool) or payout < 0:
        raise ValueError("payoutMultiplier must be an unsigned integer")
    if payout and payout % 10:
        raise ValueError("payoutMultiplier must use Stake Engine 0.1x increments")
    if not isinstance(book["events"], list):
        raise ValueError("events must be a list")
    for index, event in enumerate(book["events"]):
        if not isinstance(event, dict) or event.get("index") != index or not event.get("type"):
            raise ValueError(f"invalid event at index {index}")


def write_uncompressed_mode(output: Path, mode: BetMode, books: Iterable[dict], weights: dict[int, int]) -> dict:
    """Write validated provisional output; compression remains a separate SDK hook."""
    materialized = list(books)
    if not materialized: raise ValueError("refusing to fabricate an empty production book")
    validated_weights: dict[int, int] = {}
    for book in materialized:
        validate_book(book)
        weight = weights.get(book["id"], 1)
        if not isinstance(weight, int) or isinstance(weight, bool) or weight <= 0:
            raise ValueError("lookup weights must be positive integers")
        validated_weights[book["id"]] = weight
    output.mkdir(parents=True, exist_ok=True)
    book_name = f"books_{mode.name}.jsonl"
    lookup_name = f"lookUpTable_{mode.name}_0.csv"
    with (output / book_name).open("w", encoding="utf-8") as handle:
        for book in materialized:
            handle.write(json.dumps(book, separators=(",", ":")) + "\n")
    with (output / lookup_name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        for book in materialized:
            writer.writerow([book["id"], validated_weights[book["id"]], book["payoutMultiplier"]])
    return {"name": mode.name, "cost": mode.cost, "events": book_name, "weights": lookup_name}


def write_index(output: Path, modes: list[dict]) -> None:
    if not modes: raise ValueError("index requires at least one generated mode")
    (output / "index.json").write_text(json.dumps({"modes": modes}, indent=2) + "\n", encoding="utf-8")


def compress_jsonl(source: Path, destination: Path) -> None:
    try: import zstandard
    except ImportError as exc: raise RuntimeError("Install the official Math SDK dependencies, including zstandard, before compression") from exc
    compressor = zstandard.ZstdCompressor(level=10)
    with source.open("rb") as reader, destination.open("wb") as writer: compressor.copy_stream(reader, writer)


def _book_stream(path: Path) -> TextIO:
    if path.name.endswith(".jsonl.zst"):
        try:
            import zstandard
        except ImportError as exc:
            raise RuntimeError("Install math/requirements.txt before validating compressed books") from exc
        reader = zstandard.ZstdDecompressor().stream_reader(path.open("rb"))
        return io.TextIOWrapper(reader, encoding="utf-8")
    if path.suffix != ".jsonl":
        raise ValueError(f"unsupported result book format: {path.name}")
    return path.open("r", encoding="utf-8")


def _read_books(path: Path) -> dict[int, int]:
    books: dict[int, int] = {}
    with _book_stream(path) as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                book = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON in {path.name}:{line_number}") from exc
            validate_book(book)
            if book["id"] in books:
                raise ValueError(f"duplicate book id {book['id']} in {path.name}")
            books[book["id"]] = book["payoutMultiplier"]
    if not books:
        raise ValueError(f"result book {path.name} is empty")
    return books


def _read_lookup(path: Path) -> dict[int, tuple[int, int]]:
    rows: dict[int, tuple[int, int]] = {}
    with path.open("r", newline="", encoding="utf-8") as handle:
        for line_number, row in enumerate(csv.reader(handle), start=1):
            if len(row) != 3:
                raise ValueError(f"invalid lookup row in {path.name}:{line_number}")
            try:
                simulation_id, weight, payout = map(int, row)
            except ValueError as exc:
                raise ValueError(f"lookup values must be integers in {path.name}:{line_number}") from exc
            if simulation_id < 0 or weight <= 0 or payout < 0:
                raise ValueError(f"lookup contains invalid unsigned values in {path.name}:{line_number}")
            if payout and payout % 10:
                raise ValueError(f"lookup payout must use 0.1x increments in {path.name}:{line_number}")
            if simulation_id in rows:
                raise ValueError(f"duplicate lookup id {simulation_id} in {path.name}")
            rows[simulation_id] = (weight, payout)
    if not rows:
        raise ValueError(f"lookup {path.name} is empty")
    return rows


def _artifact_path(output: Path, filename: object) -> Path:
    if not isinstance(filename, str) or not filename:
        raise ValueError("artifact filename must be a non-empty string")
    root = output.resolve()
    path = (root / filename).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"artifact path escapes output directory: {filename}") from exc
    return path


def validate_artifacts(output: Path) -> dict:
    """Cross-check an Engine index, result books and LUTs.

    The returned RTP is an audit aid for provisional output. It is not a
    certification result.
    """
    index_path = output / "index.json"
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ValueError("index.json is missing or invalid") from exc
    if not isinstance(index, dict):
        raise ValueError("index.json must contain an object")
    modes = index.get("modes")
    if not isinstance(modes, list) or not modes:
        raise ValueError("index.json requires at least one mode")

    reports = []
    seen_names: set[str] = set()
    for mode in modes:
        required = {"name", "cost", "events", "weights"}
        if not isinstance(mode, dict) or not required.issubset(mode):
            raise ValueError("each index mode requires name, cost, events and weights")
        if mode["name"] in seen_names:
            raise ValueError(f"duplicate mode {mode['name']}")
        seen_names.add(mode["name"])
        cost = mode["cost"]
        if not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost <= 0:
            raise ValueError(f"invalid cost for mode {mode['name']}")
        book_path = _artifact_path(output, mode["events"])
        lookup_path = _artifact_path(output, mode["weights"])
        books = _read_books(book_path)
        lookup = _read_lookup(lookup_path)
        if books.keys() != lookup.keys():
            raise ValueError(f"book and lookup ids differ for mode {mode['name']}")
        for simulation_id, payout in books.items():
            if lookup[simulation_id][1] != payout:
                raise ValueError(f"payout mismatch for mode {mode['name']} id {simulation_id}")
        total_weight = sum(weight for weight, _ in lookup.values())
        weighted_payout = sum(weight * payout for weight, payout in lookup.values())
        reports.append(
            {
                "name": mode["name"],
                "bookCount": len(books),
                "totalWeight": total_weight,
                "weightedRtp": weighted_payout / total_weight / 100 / float(cost),
                "compressed": book_path.name.endswith(".jsonl.zst"),
            }
        )
    return {"modes": reports}
