"""Validate BLACK MARKET production asset provenance and content hashes."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

MEDIA_EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg", ".svg", ".mp3", ".wav", ".ogg"}
REJECTED_RELEASE_TERMS = {"prototype", "reference", "placeholder", "legacy"}


class AssetValidationError(ValueError):
    """Raised when an asset cannot be included in a production package."""


def _relative_file(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise AssetValidationError(f"{label} must be a non-empty relative path")
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise AssetValidationError(f"{label} escapes the manifest directory") from exc
    if not path.is_file():
        raise AssetValidationError(f"{label} is missing: {value}")
    if path.suffix.lower() not in MEDIA_EXTENSIONS:
        raise AssetValidationError(f"{label} is not a supported image or audio file: {value}")
    return path


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AssetValidationError(f"{label} must be a non-empty string")
    return value


def validate_manifest(manifest_path: Path, *, require_release: bool = False) -> dict[str, Any]:
    root = manifest_path.resolve().parent
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssetValidationError(f"asset manifest is missing: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise AssetValidationError("asset manifest is invalid JSON") from exc
    if not isinstance(manifest, dict) or manifest.get("schemaVersion") != 1:
        raise AssetValidationError("asset manifest schemaVersion must be 1")
    release = manifest.get("release")
    if not isinstance(release, bool):
        raise AssetValidationError("asset manifest release must be a boolean")
    if require_release and not release:
        raise AssetValidationError("release validation requires release=true")
    audio = manifest.get("audio")
    if audio not in {"none", "included"}:
        raise AssetValidationError("asset manifest audio must be 'none' or 'included'")
    entries = manifest.get("assets")
    if not isinstance(entries, list):
        raise AssetValidationError("asset manifest assets must be a list")
    if release and not entries:
        raise AssetValidationError("release asset manifest must list at least one shipped asset")

    seen: set[str] = set()
    audio_entries = 0
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise AssetValidationError(f"assets[{index}] must be an object")
        relative = _text(entry.get("path"), f"assets[{index}].path")
        if relative in seen:
            raise AssetValidationError(f"duplicate provenance entry: {relative}")
        seen.add(relative)
        path = _relative_file(root, relative, f"assets[{index}].path")
        digest = _text(entry.get("sha256"), f"assets[{index}].sha256")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != actual:
            raise AssetValidationError(f"assets[{index}].sha256 does not match {relative}")
        for field in ("creatorLicensor", "licenceGrant", "sourceFile"):
            _text(entry.get(field), f"assets[{index}].{field}")
        try:
            dt.date.fromisoformat(_text(entry.get("approvalDate"), f"assets[{index}].approvalDate"))
        except ValueError as exc:
            raise AssetValidationError(f"assets[{index}].approvalDate must be an ISO-8601 date") from exc
        if path.suffix.lower() in {".mp3", ".wav", ".ogg"}:
            audio_entries += 1
        if release and any(term in relative.lower() for term in REJECTED_RELEASE_TERMS):
            raise AssetValidationError(f"release asset path is prototype/reference-derived: {relative}")
    if audio == "none" and audio_entries:
        raise AssetValidationError("audio='none' conflicts with listed audio assets")
    if audio == "included" and not audio_entries:
        raise AssetValidationError("audio='included' requires an audio provenance entry")
    return {"assetCount": len(entries), "audio": audio, "release": release}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--release", action="store_true", help="require release=true and production-safe paths")
    args = parser.parse_args()
    try:
        report = validate_manifest(args.manifest, require_release=args.release)
    except AssetValidationError as exc:
        print(f"error: {exc}")
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
