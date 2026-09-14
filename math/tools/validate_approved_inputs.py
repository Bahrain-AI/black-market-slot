"""Validate signed, non-provisional BLACK MARKET production math inputs."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

MODES = ("base", "backroom", "vault", "black_card")
METRICS = ("maxWinFrequency", "hitRate", "volatility", "featureFrequency")


class ApprovalValidationError(ValueError):
    """Raised when supplied production math inputs cannot be approved."""


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ApprovalValidationError(f"{label} must be an object")
    return value


def _number(value: Any, label: str, *, minimum: float = 0) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < minimum:
        raise ApprovalValidationError(f"{label} must be a number >= {minimum}")
    return float(value)


def _hashed_file(root: Path, entry: Any, label: str) -> tuple[str, str]:
    entry = _object(entry, label)
    relative = entry.get("path")
    digest = entry.get("sha256")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ApprovalValidationError(f"{label}.path must be a relative file path")
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ApprovalValidationError(f"{label}.sha256 must be a lowercase SHA-256 hash")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ApprovalValidationError(f"{label}.path escapes the input directory") from exc
    if not resolved.is_file():
        raise ApprovalValidationError(f"{label}.path is missing: {relative}")
    actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
    if actual != digest:
        raise ApprovalValidationError(f"{label}.sha256 does not match {relative}")
    return relative, digest


def _validate_bounds(value: Any, label: str) -> None:
    bounds = _object(value, label)
    lower = _number(bounds.get("min"), f"{label}.min")
    upper = _number(bounds.get("max"), f"{label}.max")
    if lower > upper:
        raise ApprovalValidationError(f"{label}.min must not exceed {label}.max")


def validate_approval_manifest(manifest: Any, root: Path) -> dict[str, Any]:
    manifest = _object(manifest, "approval manifest")
    if manifest.get("schemaVersion") != 1:
        raise ApprovalValidationError("approval manifest schemaVersion must be 1")
    if manifest.get("provisional") is not False:
        raise ApprovalValidationError("approval manifest must set provisional to false")

    approval = _object(manifest.get("approval"), "approval")
    for field in ("version", "approver"):
        if not isinstance(approval.get(field), str) or not approval[field].strip():
            raise ApprovalValidationError(f"approval.{field} must be a non-empty string")
    try:
        dt.date.fromisoformat(approval.get("date"))
    except (TypeError, ValueError) as exc:
        raise ApprovalValidationError("approval.date must be an ISO-8601 date") from exc
    signed_source = _hashed_file(root, approval.get("signedSource"), "approval.signedSource")

    sources = manifest.get("sourceFiles")
    if not isinstance(sources, list) or not sources:
        raise ApprovalValidationError("sourceFiles must contain at least one hashed source file")
    hashed_sources = {_hashed_file(root, source, "sourceFiles[]") for source in sources}
    if signed_source not in hashed_sources:
        raise ApprovalValidationError("approval.signedSource must appear in sourceFiles")

    modes = _object(manifest.get("modes"), "modes")
    if set(modes) != set(MODES):
        raise ApprovalValidationError(f"modes must be exactly: {', '.join(MODES)}")
    for mode in MODES:
        values = _object(modes[mode], f"modes.{mode}")
        rtp = _number(values.get("rtp"), f"modes.{mode}.rtp")
        if not 0.90 <= rtp <= 0.98:
            raise ApprovalValidationError(f"modes.{mode}.rtp must be between 0.90 and 0.98")
        _number(values.get("cost"), f"modes.{mode}.cost", minimum=float.fromhex("0x0.0000000000001p-1022"))
    _number(manifest.get("maximumWin"), "maximumWin", minimum=float.fromhex("0x0.0000000000001p-1022"))

    par = _object(manifest.get("par"), "par")
    metric_bounds = _object(par.get("metrics"), "par.metrics")
    if set(metric_bounds) != set(MODES):
        raise ApprovalValidationError(f"par.metrics must be exactly: {', '.join(MODES)}")
    for mode in MODES:
        for metric in METRICS:
            _validate_bounds(_object(metric_bounds[mode], f"par.metrics.{mode}").get(metric), f"par.metrics.{mode}.{metric}")
    return manifest


def validate_input_directory(input_directory: Path) -> dict[str, Any]:
    root = input_directory.resolve()
    if not root.is_dir():
        raise ApprovalValidationError(f"approved input directory is missing: {root}")
    schema = root / "schema.json"
    approval_path = root / "approval.json"
    if not schema.is_file():
        raise ApprovalValidationError(f"approval schema is missing: {schema}")
    try:
        json.loads(schema.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ApprovalValidationError("approval schema is invalid JSON") from exc
    try:
        manifest = json.loads(approval_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ApprovalValidationError(f"approval manifest is missing: {approval_path}") from exc
    except json.JSONDecodeError as exc:
        raise ApprovalValidationError("approval manifest is invalid JSON") from exc
    return validate_approval_manifest(manifest, root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="directory containing schema.json and approval.json")
    args = parser.parse_args()
    try:
        approval = validate_input_directory(args.input)
    except ApprovalValidationError as exc:
        print(f"error: {exc}")
        return 1
    print(f"approved inputs valid: version={approval['approval']['version']} approver={approval['approval']['approver']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
