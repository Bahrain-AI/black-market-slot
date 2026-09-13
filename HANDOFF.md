# BLACK MARKET — Project Handoff

Last updated: 2026-09-13

Repository: `https://github.com/Bahrain-AI/black-market-slot`

Public demo: `https://raw.githack.com/Bahrain-AI/black-market-slot/main/demo/index.html`

## Current state

The browser demo **has now been rebuilt against the supplied 1671×941 luxury-auction reference**. The previous note that the demo was still the older generic presentation is obsolete.

Current demo characteristics:

- 5×4 black/gold reel grid aligned to the reference.
- Reference-derived idle tiles / game art.
- THE BLACK MARKET left-side branding.
- LOT 001 / THE UNKNOWN right-side display.
- Smoked lower HUD.
- Menu, Balance, Bet −/+, Spin, Autoplay and Turbo.
- Virtual-credit local demo outcomes.
- Spacebar spin.
- Responsive proportional scaling.

The separate production-oriented Stake Engine application remains under `src/` with its RGS/replay integration scaffold. Do not replace it with the zero-build `demo/` implementation.

## Asset state

The complete base/reference art pack is committed under:

`assets/black-market-complete-asset-pack/`

This includes:

- high-resolution GRIND. / BLACK MARKET branding masters
- exact BLACK MARKET reference image
- reference-derived symbol crops
- legacy prototype source art

Current runtime symbols/assets also exist under `assets/` and `demo/assets/` as appropriate.

## Latest addition — Bonus Buy / The Vault

Read [`BONUS-BUY.md`](BONUS-BUY.md) before implementing the next feature phase.

Prototype Buy Access modes:

- **Backroom Pass — 60× bet**
- **Vault Access — 100× bet**
- **Black Card — 200× bet**

Those prices are design targets only, not verified production values.

New web-ready special feature assets are committed under:

`assets/special-bonus/`

Files:

- `bonus-triggers.svg`
- `vault-modifiers.svg`
- `bonus-ui.svg`
- `manifest.json`
- `README.md`

Special trigger art covers:

- Scatter Crown
- Buyer
- Wild Case
- Multiplier Chip
- Red Phone
- Counterfeit Printer
- Vault Key
- EMP

Vault modifier art covers:

- Counterfeit Printer
- Golden Key
- Inside Man
- Black Card
- EMP
- Red Phone
- Double Agent
- Marked Lot

Bonus UI art covers:

- Auction Hammer
- Vault Door
- Wild Transformation
- Multiplier Increase
- Cascade Win
- Big Win

## Recommended next implementation phase

1. Add a **BUY ACCESS** button/panel to the audience demo without disturbing the reference-matched idle composition.
2. Build a premium three-card modal: Backroom Pass / Vault Access / Black Card.
3. Add a confirmation state with exact ×Bet cost.
4. Add auction-hammer → ACCESS GRANTED → vault transition.
5. Build The Vault bonus presentation using the committed trigger/modifier assets.
6. Implement demo-only feature behavior behind an explicit local-demo boundary.
7. Keep production sessions stateless and RGS-driven.
8. Build real math modes separately; do not hard-code prototype prices/probabilities into production math.

## Reference geometry

Primary design reference canvas: **1671×941**.

Approximate reel boundaries retained for QA:

```text
x: 382, 558, 735, 912, 1091, 1273
y: 109, 284, 449, 614, 779
```

Reference initial board, row-major:

```text
watch    diamond   ace       gold      cash
passport bag       bust      wild      vip
gold     cash      watch     diamond   passport
bust     wild      vip       bag       ace
```

Reference control centers:

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

## Local run

Audience demo:

```bash
git clone https://github.com/Bahrain-AI/black-market-slot.git
cd black-market-slot
python3 -m http.server 8080
```

Open:

`http://localhost:8080/demo/`

Stake Engine / Svelte app:

```bash
nvm use
npm i -g pnpm@10.5.0
pnpm install
pnpm dev
```

## Non-negotiable constraints

- Do not claim production RTP / max win / Bonus Buy pricing is final until the math package proves it.
- Do not fabricate Stake Engine books/LUTs.
- Preserve the reference-matched demo visual quality while adding features.
- Preserve RGS/replay integration under `src/`.
- Keep audience-demo outcomes clearly separate from production behavior.
- Keep runtime assets local; no external CDN dependency.
