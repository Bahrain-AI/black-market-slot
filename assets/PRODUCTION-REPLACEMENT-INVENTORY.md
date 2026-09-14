# BLACK MARKET production replacement inventory

Status: blocked pending final artwork and provenance records. Every listed
runtime file must be an original final deliverable, locally stored, and listed
with its SHA-256, creator/licensor, licence grant, approval date, and source
file in `assets/PRODUCTION-LICENSES.json` before a release build.

## Runtime symbols

Replace these ten WebPs under `assets/symbols/`: `ace.webp`, `bag.webp`,
`bust.webp`, `cash.webp`, `diamond.webp`, `gold.webp`, `passport.webp`,
`vip.webp`, `watch.webp`, and `wild.webp`. The current files are
reference-derived placeholders and cannot be accepted by release mode.

## Animation source sets

Replace every source frame under the named `assets/anim-frames/` directory,
then provide the resulting local WebP, TexturePacker-compatible JSON, and a
static first-frame PNG for review.

| Source directory | Required result | Sheet / frame dimensions | Required states |
| --- | --- | --- | --- |
| `symbol-wild-expand/` | `assets/animations/symbol-wild-expand.webp` + JSON | 1024×1024 / 256×256 | idle, anticipation, expand-start, expand-loop, settle |
| `symbol-scatter-freespins/` | `assets/animations/symbol-scatter-freespins.webp` + JSON | 1536×512 / 256×256 | idle, land, trigger, retrigger, glow-loop |
| `ui-freespins-multiplier/` | `assets/animations/ui-freespins-multiplier.webp` + JSON | 1024×512 / 256×256 | 1×, 2×, 3×, 5×, 10×, pulse |
| `symbol-hold-lock/` | `assets/animations/symbol-hold-lock.webp` + JSON | 1536×768 / 256×256 | idle values, land, lock, value-update, multiplier-update, collect |
| `frame-hold-spin/` | `assets/animations/frame-hold-spin.webp` + JSON | 2048×1024 / 512×512 | enter, idle-loop, new-lock, final-respin, exit |
| `fx-cascade-remove/` | `assets/animations/fx-cascade-remove.webp` + JSON | 2048×1024 / 256×256 | mark, fracture, dissolve, clear |
| `fx-reel-refill/` | `assets/animations/fx-reel-refill.webp` + JSON | 2048×1024 / 256×256 | drop-start, trail, impact, settle |
| `fx-multiplier-increase/` | `assets/animations/fx-multiplier-increase.webp` + JSON | 2048×1024 / 256×256 | charge, burst, tier-change, settle |

The first seven rows are the requested Wild, Scatter, multiplier badge, Hold
& Spin symbol/frame, cascade, and refill sets. The mechanics specification
also explicitly requires `fx-multiplier-increase/`; it is included here so a
submission cannot omit a specified runtime effect.

## Tile artwork and logo

Provide final, non-reference source files for the release tile builder:

- Background source for `BlackMarket-BG.png`, rendered to 1280×720.
- RGBA foreground source for `BlackMarket-FG.png`, rendered to 1280×720 with
  transparency.
- Approved transparent provider-logo source for `GrindStudios-Logo.png`.

The three output PNGs together must be no larger than 3 MB. Release mode
requires explicit `--background`, `--foreground`, and `--logo` source paths
and rejects paths containing `prototype`, `reference`, `placeholder`, or
`legacy`.

## Audio

Provide each runtime audio file with a provenance record, or retain the
explicit `"audio": "none"` declaration in `assets/PRODUCTION-LICENSES.json`.
No external runtime asset URL is permitted.
