"""Generate the Stake Engine tile package (BG / FG / provider logo) for BLACK MARKET.

Outputs into `stake-engine/tile-package/` from committed art sources and verifies
the Engine constraint that the combined tile size is <= 3 MB.

These are presentation tiles derived from committed artwork. They are placeholders
until the final approved artwork/asset licensing pass is completed.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "stake-engine" / "tile-package"
REFERENCE = REPO / "assets" / "black-market-complete-asset-pack" / "reference" / "black-market-reference.png"
ARTIFACT = REPO / "assets" / "black-market-complete-asset-pack" / "legacy-prototype" / "assets" / "artifact.png"
GRIND_LOGO = REPO / "branding" / "grind-mark.webp"
GRIND_LOGO_SHEET = REPO / "branding" / "grind-logo-sheet.webp"

WIDTH, HEIGHT = 1280, 720
MAX_TOTAL_BYTES = 3 * 1024 * 1024  # Engine tile package limit
REJECTED_RELEASE_TERMS = ("prototype", "reference", "placeholder", "legacy")


class TileSourceError(ValueError):
    """Raised when a release tile attempts to use non-production artwork."""


def validate_release_sources(background: Path | None, foreground: Path | None, logo: Path | None) -> None:
    for label, source in (("background", background), ("foreground", foreground), ("logo", logo)):
        if source is None or not source.is_file():
            raise TileSourceError(f"release tile builder requires a final {label} file")
        lower_path = source.as_posix().lower()
        blocked_term = next((term for term in REJECTED_RELEASE_TERMS if term in lower_path), None)
        if blocked_term:
            raise TileSourceError(f"release tile builder refuses {blocked_term} source: {source}")


def _make_bg(source: Path, output: Path) -> Path:
    image = Image.open(source).convert("RGB")
    image = ImageOps.fit(image, (WIDTH, HEIGHT), Image.LANCZOS)
    target = output / "BlackMarket-BG.png"
    image.save(target, "PNG", optimize=True)
    return target


def _make_fg(source: Path | None, output: Path) -> Path:
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    if source is not None and source.is_file():
        artifact = Image.open(source).convert("RGBA")
        artifact = ImageOps.contain(artifact, (400, 400), Image.LANCZOS)
        canvas.paste(artifact, (WIDTH - artifact.width - 90, HEIGHT - artifact.height - 60), artifact)
    target = output / "BlackMarket-FG.png"
    canvas.save(target, "PNG", optimize=True)
    return target


def _make_logo(source: Path, output: Path) -> Path:
    logo = Image.open(source).convert("RGBA")
    logo = ImageOps.contain(logo, (512, 512), Image.LANCZOS)
    target = output / "GrindStudios-Logo.png"
    logo.save(target, "PNG", optimize=True)
    return target


def build(
    *,
    output: Path = OUTPUT,
    release: bool = False,
    background: Path | None = None,
    foreground: Path | None = None,
    logo: Path | None = None,
) -> dict:
    if release:
        validate_release_sources(background, foreground, logo)
    background = background or REFERENCE
    foreground = foreground or ARTIFACT
    logo = logo or (GRIND_LOGO_SHEET if GRIND_LOGO_SHEET.is_file() else GRIND_LOGO)
    output.mkdir(parents=True, exist_ok=True)
    files = [_make_bg(background, output), _make_fg(foreground, output), _make_logo(logo, output)]
    result = {}
    for path in files:
        size = path.stat().st_size
        with Image.open(path) as image:
            result[path.name] = {"bytes": size, "width": image.width, "height": image.height}
    total = sum(entry["bytes"] for entry in result.values())
    result["_totalBytes"] = total
    result["_withinEngineLimit"] = total <= MAX_TOTAL_BYTES
    if not result["_withinEngineLimit"]:
        raise RuntimeError(f"tile package exceeds the 3 MB Engine limit: {total} bytes")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--release", action="store_true", help="require final non-reference source files")
    parser.add_argument("--background", type=Path)
    parser.add_argument("--foreground", type=Path)
    parser.add_argument("--logo", type=Path)
    args = parser.parse_args()
    import json

    print(
        json.dumps(
            build(
                output=args.output,
                release=args.release,
                background=args.background,
                foreground=args.foreground,
                logo=args.logo,
            ),
            indent=2,
        )
    )
