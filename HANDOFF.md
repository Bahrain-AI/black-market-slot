# BLACK MARKET — Project Handoff

Last updated: 2026-09-14

## Phase 1 Stake Engine architecture

The production path now uses Svelte 5 for wallet/UI lifecycle and one PixiJS 8 Application for reels, symbols, and ordered feature playback. Typed events and reducers cover cascades, expanding Wilds, Free Spins with the configured `1× → 2× → 3× → 5× → 10×` progression, and persistent Hold & Spin locks. `src/game/engine/demoRounds.ts` is the only production-source demo fixture; RGS and replay sessions consume supplied event books without frontend outcome RNG.

The Python package under `math/black_market/` mirrors the frontend contract and provides Phase 1 calculation/state/output interfaces. It is not final production math. Official SDK integration, production simulations, RTP optimization, compression validation, and Engine staging remain required.

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

## Latest addition — Stake Engine SDK game overlay

The provisional BLACK MARKET overlay for the pinned official Stake Engine Math SDK now lives repository-side under `math/sdk_game/black_market/`:

- `game_config.py` — SDK-native `Config` subclass: 5×4 board, symbols (H1–H4, L1–L4, W, S, P), provisional paytable, provisional reels (`BR0`/`FR0`/`HR0`), base-game / Free Spins (`1× → 2× → 3× → 5× → 10×`) / Hold & Spin distributions, BetModes for all Bonus Buy modes (base, backroom, vault, black_card), `wincap` max-win and provisional RTP (0.96) hooks, `provisional = True`.
- `game_events.py` — maps all 16 frontend event types through the SDK `book.add_event` interface with monotonic indices and the exact payload keys the frontend `src/game/events/types.ts` contract requires.
- `reels/*.csv` — provisional weighted reel inputs (not approved production strips).

`python math/tools/bootstrap_sdk.py` now stages the overlay into the pinned checkout (`games/black_market/`) after revision validation, and `python math/tools/smoke_sdk_game.py` proves the staged `GameConfig` instantiates against the pinned SDK and that every frontend event maps correctly. All overlay values remain configuration-driven and explicitly provisional; nothing here is certified production math.

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
