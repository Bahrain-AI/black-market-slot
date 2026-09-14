"""Pinned official Stake Engine Math SDK checkout integration."""

import ast
from pathlib import Path
import subprocess

SDK_REPOSITORY = "https://github.com/StakeEngine/math-sdk.git"
SDK_COMMIT = "307e6812b38489e212f835001f21e9f7d4c18a4d"
SDK_REQUIRED_FILES = (
    "src/config/config.py",
    "src/config/betmode.py",
    "src/events/events.py",
    "src/state/run_sims.py",
    "src/write_data/write_configs.py",
    "utils/rgs_verification.py",
)
SDK_REQUIRED_SYMBOLS = {
    "src/config/config.py": {"Config"},
    "src/config/betmode.py": {"BetMode"},
    "src/events/events.py": {"reveal_event", "set_total_event", "set_win_event"},
    "src/state/run_sims.py": {"create_books"},
    "src/write_data/write_configs.py": {"generate_configs"},
    "utils/rgs_verification.py": {"execute_all_tests"},
}


def _checkout_revision(root: Path, allow_revision_marker: bool) -> str:
    marker = root / ".stake-engine-revision"
    if allow_revision_marker and marker.is_file():
        return marker.read_text(encoding="utf-8").strip()
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"{root} is not a readable Git checkout") from exc


def validate_sdk_checkout(root: Path, *, allow_revision_marker: bool = False) -> dict[str, object]:
    root = root.resolve()
    revision = _checkout_revision(root, allow_revision_marker)
    if revision != SDK_COMMIT:
        raise ValueError(f"Stake Engine Math SDK revision must be {SDK_COMMIT}; found {revision}")
    missing = [relative for relative in SDK_REQUIRED_FILES if not (root / relative).is_file()]
    if missing:
        raise ValueError(f"Stake Engine Math SDK checkout is missing: {', '.join(missing)}")
    missing_symbols: list[str] = []
    for relative, required in SDK_REQUIRED_SYMBOLS.items():
        module = ast.parse((root / relative).read_text(encoding="utf-8"), filename=relative)
        available = {
            node.name
            for node in module.body
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        }
        missing_symbols.extend(f"{relative}:{name}" for name in sorted(required - available))
    if missing_symbols:
        raise ValueError(f"Stake Engine Math SDK interfaces changed or are missing: {', '.join(missing_symbols)}")
    return {
        "repository": SDK_REPOSITORY,
        "commit": revision,
        "root": str(root),
        "requiredFiles": len(SDK_REQUIRED_FILES),
        "requiredSymbols": sum(len(symbols) for symbols in SDK_REQUIRED_SYMBOLS.values()),
    }
