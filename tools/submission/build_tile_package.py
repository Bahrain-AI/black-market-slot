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


def _make_bg() -> Path:
    image = Image.open(REFERENCE).convert("RGB")
    image = ImageOps.fit(image, (WIDTH, HEIGHT), Image.LANCZOS)
    target = OUTPUT / "BlackMarket-BG.png"
    image.save(target, "PNG", optimize=True)
    return target


def _make_fg() -> Path:
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    if ARTIFACT.is_file():
        artifact = Image.open(ARTIFACT).convert("RGBA")
        artifact = ImageOps.contain(artifact, (400, 400), Image.LANCZOS)
        canvas.paste(artifact, (WIDTH - artifact.width - 90, HEIGHT - artifact.height - 60), artifact)
    target = OUTPUT / "BlackMarket-FG.png"
    canvas.save(target, "PNG", optimize=True)
    return target


def _make_logo() -> Path:
    source = GRIND_LOGO_SHEET if GRIND_LOGO_SHEET.is_file() else GRIND_LOGO
    logo = Image.open(source).convert("RGBA")
    logo = ImageOps.contain(logo, (512, 512), Image.LANCZOS)
    target = OUTPUT / "GrindStudios-Logo.png"
    logo.save(target, "PNG", optimize=True)
    return target


def build() -> dict:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    files = [_make_bg(), _make_fg(), _make_logo()]
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
    args = parser.parse_args()
    if args.output != OUTPUT:
        OUTPUT = args.output
    import json

    print(json.dumps(build(), indent=2))