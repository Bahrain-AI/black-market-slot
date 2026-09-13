# BLACK MARKET — Bonus Buy / Vault Feature

Status: **visual + gameplay design specification; production math pending**.

The Bonus Buy system should feel like purchasing access to increasingly restricted rooms of the underground auction, not like a generic slot feature menu.

## Buy modes

| Mode | Prototype price | Entry | Identity |
| --- | ---: | --- | --- |
| **BACKROOM PASS** | **60× bet** | Immediate Bid War | Entry-level high-volatility access |
| **VAULT ACCESS** | **100× bet** | The Vault — 8 bonus spins | Choose 1 persistent modifier from 3 |
| **BLACK CARD** | **200× bet** | Premium Vault | 2 modifiers active + boosted starting multiplier |

Prices above are **prototype targets only**. Final buy cost, RTP, hit rate, volatility and max exposure must come from the verified production math package.

## Special in-bonus symbols

- **SCATTER / CROWN** — triggers or upgrades the bonus state.
- **BUYER** — converts selected symbols into WILDs.
- **WILD CASE** — spawns one or more WILD positions.
- **MULTIPLIER CHIP** — raises the active multiplier; planned visual tiers: `×2`, `×3`, `×5`, `×10`, `×25`.
- **RED PHONE** — applies a random multiplier upgrade.
- **COUNTERFEIT PRINTER** — duplicates a selected winning symbol.
- **VAULT KEY** — unlocks/injects a premium symbol.
- **EMP** — removes low-value symbols before the next evaluation.

## Vault modifier pool

- **Counterfeit Printer** — persistent duplicate-symbol modifier.
- **Golden Key** — guarantees or boosts premium symbols.
- **Inside Man** — increases Buyer appearances.
- **Black Card** — starts bonus spins at a higher multiplier.
- **EMP** — strips low-value symbols.
- **Red Phone** — upgrades win multipliers.
- **Double Agent** — upgrades two symbols instead of one.
- **Marked Lot** — enhances one reel/position for the full bonus.

## Presentation sequence

1. Player opens **BUY ACCESS**.
2. Three premium cards appear: Backroom Pass / Vault Access / Black Card.
3. Confirmation shows the exact cost in ×Bet and currency.
4. Auction hammer drops.
5. Room lighting dims and the vault animation begins.
6. `ACCESS GRANTED` resolves in champagne gold.
7. Bonus starts with the selected mode/modifiers.

Keep this sequence restrained and premium: short transitions, gallery lighting, black marble, smoked glass, champagne gold and deep burgundy accents. Avoid generic neon casino effects.

## Assets

Web-ready special feature assets are under [`assets/special-bonus/`](assets/special-bonus/):

- `bonus-triggers.svg`
- `vault-modifiers.svg`
- `bonus-ui.svg`
- `manifest.json`

The base/reference/branding master assets remain under `assets/black-market-complete-asset-pack/` and `branding/`.

## Stake Engine math note

Each purchasable feature should ultimately map to a separately verified game mode / outcome-book configuration. The frontend must not invent feature results, pricing, RTP or probability behavior during production sessions.
