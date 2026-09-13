<p align="center">
  <img src="branding/black-market-cover.webp" alt="BLACK MARKET — by GRIND." width="760" />
</p>

<h1 align="center">BLACK MARKET</h1>

<p align="center"><strong>A premium auction-house slot concept by GRIND.</strong></p>

<p align="center">
  <a href="https://raw.githack.com/Bahrain-AI/black-market-slot/main/demo/index.html"><strong>▶ PLAY THE PUBLIC DEMO</strong></a>
</p>

<p align="center">
  <strong>RARE ITEMS. BIGGER STORIES.</strong><br/>
  Stake Engine-ready frontend · Svelte 5 · Vite · Responsive · RGS integration scaffold
</p>

---

## Overview

**BLACK MARKET** is a luxury underground-auction slot built around rare objects, escalating bids and high-stakes presentation. The visual language combines black marble, smoked glass, champagne gold and gallery lighting with a restrained premium interface.

This repository contains the playable frontend, a zero-build public demo, GRIND. provider branding, complete reference/base asset pack, Stake Engine integration layer, Bonus Buy/Vault feature design, submission notes and the foundation for the production math package.

> **Current status:** reference-matched playable prototype with a working local Bonus Buy / Vault prototype + Stake Engine integration scaffold. Final certified math, RTP, volatility, max exposure and Bonus Buy pricing remain pending validation/simulation.

## Play it

**Live audience demo:** https://raw.githack.com/Bahrain-AI/black-market-slot/main/demo/index.html

The public demo is intentionally separated from the production Stake Engine path. It uses virtual credits and local demo outcomes only so visitors can experience the visual direction and interaction without an RGS session.

> **Rebuilt 1:1 against the luxury-auction reference:** the demo matches the supplied 1671×941 reference board with the exact 5×4 black/gold reel geometry, reference-derived idle artwork, THE BLACK MARKET branding, LOT 001, and the smoked HUD with Menu / Balance / Bet / Spin / Autoplay / Turbo.

## GRIND. — provider identity

<p align="center">
  <img src="branding/grind-logo-sheet.webp" alt="GRIND. logo system" width="720" />
</p>

**Provider:** Grind Studios  
**Consumer brand:** **GRIND.**  
**Tagline:** **Distinct by Design.**

The working brand kit is in [`branding/`](branding/), while high-resolution generated masters and the exact reference pack are under [`assets/black-market-complete-asset-pack/`](assets/black-market-complete-asset-pack/).

## Core game direction

- Premium 5×4 slot presentation
- Luxury underground-auction theme
- WILD substitution
- Reference-matched browser demo
- Responsive desktop/mobile/popout layout
- Keyboard spin support
- Turbo / autoplay in the audience demo
- RGS-controlled balance, currency and bet levels in the Engine path
- Replay-mode support
- Local assets only; no runtime CDN dependency

Signature systems include **Bid War**, **Steal or Sell**, **The Vault**, and **Bonus Buy / Buy Access**.

## Bonus Buy / The Vault

The public demo now has a working local **BUY ACCESS** prototype. Click the BUY label on the left side of the reference scene or press **B**.

Prototype modes:

- **BACKROOM PASS — 60× bet** — 6 bonus spins with elevated special-symbol frequency.
- **VAULT ACCESS — 100× bet** — 8 bonus spins with one persistent Vault modifier.
- **BLACK CARD — 200× bet** — 10 bonus spins, a 3× starting multiplier and two persistent modifiers.

The bonus can trigger Scatter extra spins, Buyer WILD conversion, Wild Case spawns, multiplier chips, Red Phone multipliers, Counterfeit duplication, Vault Key premium upgrades and EMP low-symbol removal. Persistent Vault modifiers include Counterfeit Printer, Golden Key, Inside Man, EMP, Red Phone, Double Agent and Marked Lot.

Web-ready feature art is under [`assets/special-bonus/`](assets/special-bonus/):

- `bonus-triggers.svg` — Scatter, Buyer, Wild Case, Multiplier, Red Phone, Counterfeit Printer, Vault Key, EMP.
- `vault-modifiers.svg` — Counterfeit Printer, Golden Key, Inside Man, Black Card, EMP, Red Phone, Double Agent, Marked Lot.
- `bonus-ui.svg` — Auction Hammer, Vault Door, Wild Transformation, Multiplier Increase, Cascade Win, Big Win.
- `manifest.json` — atlas layout and intended feature behavior.
- [`BONUS-BUY.md`](assets/special-bonus/BONUS-BUY.md) — browser-ready asset/feature map.

These are visual/prototype mechanics only. Final costs and probabilities must come from verified production math.

## Stake Engine integration

The frontend is structured for Stake Engine launch parameters and wallet communication, including:

- `sessionID`
- `rgs_url`
- `lang`
- `device`
- `/wallet/authenticate`
- `/wallet/play`
- `/wallet/end-round`
- replay query parameters and `/bet/replay/...`
- jurisdiction-aware Turbo visibility

See [`stake-engine/README.md`](stake-engine/README.md) and [`stake-engine/submission-checklist.md`](stake-engine/submission-checklist.md).

## Tech stack

- **Svelte 5**
- **Vite**
- **TypeScript / JavaScript**
- Static production build
- Stake Engine RGS integration scaffold
- Plain HTML/CSS/JS zero-build audience demo

## Local development

For the audience demo:

```bash
python3 -m http.server 8080
```

Open `http://localhost:8080/demo/`.

For the Svelte / Stake Engine application:

```bash
nvm use
npm i -g pnpm@10.5.0
pnpm install
pnpm dev
```

Without Engine launch parameters, the Svelte app runs in a clearly separated local demo mode for frontend development. Production sessions are intended to obtain outcomes from the RGS.

## Production build

```bash
pnpm build
```

The resulting `dist/` directory is the static frontend bundle intended for Engine deployment/submission.

## Math status

The production math package is intentionally **not fabricated**. Stake Engine requires verified static outcome books and weighted lookup tables.

See [`math/README.md`](math/README.md).

Before submission we still need to:

1. Finish the actual game math model, including each Bonus Buy game mode.
2. Run large-scale simulations for each production mode.
3. Optimize and verify RTP / volatility / max-win behavior.
4. Generate final weighted lookup tables and outcome books.
5. Replace prototype rules/feature-price copy with verified values.
6. Complete final staging, mobile and replay QA.

## Repository structure

```text
BONUS-BUY.md     Buy Access / Vault feature specification
HANDOFF.md       current continuation state and next steps
branding/        GRIND. identity + cover previews
demo/            reference-matched zero-build audience demo + Bonus Buy
math/            math package notes / production math work
src/             Svelte application source
stake-engine/    Engine integration + submission checklist
assets/          base game, full generated masters, reel art and bonus assets
```

## Disclaimer

This project is in active development and is **not yet a certified or production-approved gambling product**. Final gameplay probabilities, RTP, paytable values, feature pricing and release assets must be validated before submission or public wagering use.

---

<p align="center"><strong>BLACK MARKET — by GRIND.</strong><br/>Distinct by Design.</p>
