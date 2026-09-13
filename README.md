# BLACK MARKET — Stake Engine game

Premium minimalist 5×4 slot frontend prepared for Stake Engine RGS integration.

## Provider branding

**Provider:** Grind Studios  
**Consumer brand:** **GRIND.**  
**Tagline:** **Distinct by Design.**

Provider identity and current creative assets live in [`branding/`](branding/):

- [`BRAND.md`](branding/BRAND.md) — brand system and logo-animation direction
- [`grind-mark.webp`](branding/grind-mark.webp) — standalone broken-G mark
- [`grind-logo-sheet.webp`](branding/grind-logo-sheet.webp) — wordmark / lockup reference
- [`grind-logo-animation-storyboard.webp`](branding/grind-logo-animation-storyboard.webp) — six-stage reveal concept
- [`black-market-cover.webp`](branding/black-market-cover.webp) — current BLACK MARKET cover direction

These repo images are optimized working previews. Keep the original high-resolution generated masters for final Engine submission/export.

## Stack

- Svelte 5
- Vite static build
- Stake Engine RGS wallet flow
- Engine replay mode
- Responsive desktop/mobile/popout layout
- Local game assets only; no runtime CDN dependencies

## Development

```bash
nvm use
npm i -g pnpm@10.5.0
pnpm install
pnpm dev
```

Without Engine launch parameters the app runs in a clearly separated local demo mode for frontend development. Production sessions always obtain outcomes from the RGS.

## Build for Engine

```bash
pnpm build
```

Upload the complete `dist/` folder as the Engine Front End build.

## Engine integration

See [`stake-engine/README.md`](stake-engine/README.md) and [`stake-engine/submission-checklist.md`](stake-engine/submission-checklist.md).

The frontend supports:

- `sessionID`, `rgs_url`, `lang`, and `device` launch parameters
- `/wallet/authenticate`
- `/wallet/play`
- `/wallet/end-round`
- RGS-controlled balance, currency and bet levels
- replay query parameters and `/bet/replay/...`
- jurisdiction-aware Turbo visibility
- Spacebar spin
- rules/info and sound controls

## Math status

The final production math package is intentionally not fabricated. Stake Engine requires verified static outcome books and weighted lookup tables. See [`math/README.md`](math/README.md).

Before submission, generate and optimize the real math model, then replace the provisional RTP/paytable text in the game rules with the verified values. Engine recommends 100k+ diverse simulations per production mode before optimization.
