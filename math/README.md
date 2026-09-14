# BLACK MARKET math

Stake Engine requires pre-generated, stateless outcomes. Production math should be generated with the official `StakeEngine/math-sdk` (recommended) or another generator that emits the exact Engine publication format.

## Target design

- Mode: `base`
- Cost multiplier: `1.0`
- Target RTP: `0.96` (96.00%)
- Target max win: `5000x`
- Board: 5 reels × 4 rows
- Stateless rounds only

Phase 1 logic lives under `math/black_market/` and mirrors the frontend event contract for cascades, expanding Wilds, Free Spins, multiplier progression, and Hold & Spin. It includes deterministic calculation helpers, persistent feature state, mode configuration, JSONL/lookup/index writers, Zstandard compression, and full cross-file validation.

The official SDK integration is pinned to commit `307e6812b38489e212f835001f21e9f7d4c18a4d`. The bootstrap command creates a local, ignored checkout and refuses a different revision:

```text
python -m pip install -r math/requirements.txt
python math/tools/bootstrap_sdk.py
```

This repository does not copy or silently drift the SDK runtime. BLACK MARKET's final SDK `GameConfig`, reel strips, paytable, distributions, and optimized weights remain pending approved math design and large-scale simulation.

## SDK game overlay

The repository-owned provisional overlay under `math/sdk_game/black_market/` is the BLACK MARKET single source for the SDK game configuration:

- `game_config.py` — SDK `Config` subclass: 5×4 board, symbol configuration, provisional paytable, provisional reel inputs (`BR0`/`FR0`/`HR0`), base/Free Spins/Hold & Spin distributions, BetMode definitions matching the Bonus Buy modes (base, backroom, vault, black_card), and the max-win / provisional-RTP hooks (`wincap`, `rtp`, `provisional`).
- `game_events.py` — deterministic event mapping into the frontend contract (`reveal` … `roundEnd`), emitting through the SDK-shaped `book.add_event` interface.
- `reels/*.csv` — provisional weighted reel inputs, clearly not approved production strips.

Staging and smoke check (requires the local pinned checkout from `bootstrap_sdk.py`):

```text
python math/tools/bootstrap_sdk.py
python math/tools/smoke_sdk_game.py
```

`bootstrap_sdk.py` stages the overlay into the checkout (`games/black_market/`) after validating the pinned revision. The smoke test instantiates `GameConfig` inside the staged checkout and asserts the configuration, all Bonus Buy modes, and the complete frontend event mapping. Generated SDK checkouts are ignored by Git.

The repository does **not** contain fabricated production math. Final RTP, hit rate, volatility, payout table, and max-win frequency must be produced and verified from the approved simulation set before submission.

## Required publication output

Place final Engine-uploadable files under `math/publish_files/`:

```text
math/publish_files/
├── index.json
├── books_base.jsonl.zst
└── lookUpTable_base_0.csv
```

`index.json` must have the Engine format:

```json
{
  "modes": [
    {
      "name": "base",
      "cost": 1.0,
      "events": "books_base.jsonl.zst",
      "weights": "lookUpTable_base_0.csv"
    }
  ]
}
```

Each JSONL result must contain `id`, `events`, and `payoutMultiplier`. Payout multipliers use integer hundredths (`100` = `1.00x`) and non-zero values use the SDK/RGS `0.1x` increment. Lookup rows contain unsigned integer values in the order `simulation_id,weight,payout_multiplier`, and the payout multiplier must exactly match the corresponding book result.

Engine recommends 100k+ production simulations per mode to create sufficient outcome diversity before optimization. Generate PAR/statistical output and verify RTP and max-win frequency before uploading math to ACP.

## Phase 1 verification

```text
python -m unittest discover -s math/tests -v
cd math && python -m black_market.run
python math/tools/validate_artifacts.py <artifact-directory>
```

The validator reads uncompressed or `.jsonl.zst` books, validates every event sequence, checks unique IDs and unsigned lookup fields, proves payout equality between each book and lookup row, and reports weighted RTP as a provisional audit value. Production `index.json` entries must reference compressed books. Generated SDK checkouts and math artifacts are ignored by Git.
