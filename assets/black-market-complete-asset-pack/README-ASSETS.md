# BLACK MARKET — Complete Asset Pack

This pack consolidates the clean visual assets currently available for the BLACK MARKET browser-demo handoff.

## Use these first

### `reference/`
- `black-market-reference.png` — exact 1671×941 user-supplied target image. This is the primary visual truth source.
- `black-market-reference.webp` — optimized 1671×941 copy for browser use.
- `reference-preview.webp` — lighter preview.

### `symbols/`
Reference-derived crops for the 10 visible symbol types:
- watch
- diamond
- ace
- gold
- cash
- passport
- bag
- bust
- wild
- vip

These are intended to replace the simple SVG placeholders when reproducing the screenshot closely.

### `branding/`
High-resolution GRIND. / BLACK MARKET creative masters:
- `grind-logo-sheet.png`
- `grind-mark.png`
- `grind-logo-animation-storyboard.png`
- `black-market-cover.png`

## `legacy-prototype/`
The raster assets from the first BLACK MARKET prototype, preserved as fallback/source material:
- background.jpg
- logo.png
- artifact.png
- reference.jpg
- 10 PNG symbol images

## Recommended repo placement

After cloning `Bahrain-AI/black-market-slot`, copy the clean assets into a normal folder such as:

```text
demo/assets/reference.png
demo/assets/reference.webp
demo/assets/symbols/*.webp
demo/assets/branding/*.png
```

Then rebuild `demo/index.html`, `demo/style.css`, and `demo/game.js` around those normal assets. The existing `demo/ref/*.js` encoded chunks are WIP transport artifacts and can be removed once the clean reference image is committed normally.

## Important

The public demo currently in the repository is not yet the finished 1:1 implementation. The production Stake Engine/RGS code under `src/` should remain separate and intact.
