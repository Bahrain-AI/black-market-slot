# BLACK MARKET — Project Handoff

Last updated: 2026-09-13

## Goal

Continue the BLACK MARKET slot prototype and rebuild the public browser demo to match the supplied luxury-auction reference image as closely as possible while keeping it genuinely playable.

Repository: `https://github.com/Bahrain-AI/black-market-slot`

Public demo URL: `https://raw.githack.com/Bahrain-AI/black-market-slot/main/demo/index.html`

## Important current state

The current public demo is still the earlier audience demo. It is **not yet the 1:1 reference-matched implementation**.

The existing live demo files are:

- `demo/index.html`
- `demo/style.css`
- `demo/game.js`

Reference-image payload chunks from the previous reconstruction attempt are already committed under:

- `demo/ref/`

Do not assume those chunks are already wired correctly. The currently committed `demo/index.html` does not use them.

The separate Stake Engine application lives under `src/` and should not be confused with the public static demo. Preserve the Stake Engine/RGS work while rebuilding `demo/`.

## Reference composition

Original reference canvas: **1671 × 941 px** (~16:9).

The browser demo should preserve this exact aspect ratio and scale the complete scene as one stage. Avoid responsive reflow of individual objects on desktop; scale the stage proportionally instead.

Approximate reel-grid pixel boundaries on the 1671×941 reference:

```text
x: 382, 558, 735, 912, 1091, 1273
y: 109, 284, 449, 614, 779
```

This yields a 5×4 grid occupying approximately:

```text
left:   22.86%
top:    11.58%
width:  53.32%
height: 71.20%
```

Use these boundaries as the starting point, then visually tune by a few pixels against the reference.

### Reference symbols

The visible reference board uses these 10 symbol types:

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

Initial visual board in the reference, row-major:

```text
watch    diamond   ace       gold      cash
passport bag       bust      wild      vip
gold     cash      watch     diamond   passport
bust     wild      vip       bag       ace
```

For the closest match, crop/extract the actual visual symbol tiles from the reference image instead of using the simple SVG placeholders in `assets/symbols/`.

## Control layout

Approximate control centers on the 1671×941 reference:

```text
menu       231, 847
balance    360, 847
minus      604, 847
bet        714, 847
plus       825, 847
spin       1102, 842
autoplay   1250, 847
turbo      1400, 847
```

Suggested click/hit rectangles:

```text
menu       x188  y803  w82   h84
minus      x574  y816  w62   h62
plus       x794  y816  w62   h62
spin       x1034 y777  w138  h138
autoplay   x1178 y813  w148  h66
turbo      x1334 y813  w132  h66
```

Convert to percentages so the controls scale with the reference stage.

## Required demo behavior

The reference-matched demo should support:

- Spin button
- Spacebar spin
- Bet − / +
- Turbo toggle
- Autoplay toggle
- Menu / game-info modal
- Balance deduction and win credit
- Reel/symbol animation
- Highlighted wins
- Responsive scale-down on mobile without destroying the reference composition

Suggested demo balance/bet defaults:

```text
balance: 991.30
bet: 1.00
bet steps: [0.10, 0.20, 0.50, 1, 2, 5, 10]
```

This is an audience prototype only. Do not imply that the production math, RTP, max win, or certification is final.

## Visual target

Match the reference, not the older generic demo styling:

- warm daylight luxury auction hall
- cream marble floor
- tall arched windows
- black/gold reel frame
- exact 5×4 tile proportions
- left-side THE BLACK MARKET title block
- right-side vertical slogan and LOT 001 display
- smoked translucent bottom HUD
- oversized circular Spin button
- compact pill-shaped Autoplay and Turbo buttons
- typography, spacing, shadows and gold tone as close as practical

The idle state should be visually almost indistinguishable from the reference screenshot at the same aspect ratio.

## Recommended implementation approach

1. Use the reference screenshot as the compositional base layer during reconstruction.
2. Rebuild the reel grid as a precise absolute-position overlay.
3. Crop the 10 symbol tile appearances from the reference into dedicated assets.
4. Place interactive symbols in the exact tile rectangles.
5. Recreate/patch the HUD text areas so Balance and Bet can update dynamically without visibly diverging from the reference.
6. Use invisible absolute-position hit targets over Menu, −, +, Spin, Autoplay and Turbo.
7. Add short premium animations only; avoid flashy generic casino effects.
8. Test at 1671×941 first, then 1440×810, 1920×1080, and mobile landscape.

## Local run

The `demo/` directory is plain static HTML/CSS/JS, so no package install is required for it.

```bash
git clone https://github.com/Bahrain-AI/black-market-slot.git
cd black-market-slot
python3 -m http.server 8080
```

Open:

```text
http://localhost:8080/demo/
```

For the Svelte/Stake Engine app:

```bash
nvm use
npm i -g pnpm@10.5.0
pnpm install
pnpm dev
```

## Acceptance criteria for the next agent

Do not call the work complete until:

1. The idle browser screenshot is extremely close to the supplied reference at 1671×941.
2. All 20 reel cells align with the reference grid.
3. Spin, Bet −/+, Turbo, Autoplay and Menu are functional.
4. The initial board exactly matches the reference image.
5. The interface remains usable in mobile landscape and scales proportionally.
6. `demo/` contains no external runtime dependencies.
7. The existing Stake Engine integration under `src/` is not broken.
8. The public raw.githack URL works after commit.

## Known caution

The current `demo/ref/*.js` files are WIP encoded reference-image chunks from an interrupted approach. Inspect them before deciding whether to reuse or delete them. A cleaner implementation may replace them with normal optimized WebP assets.
