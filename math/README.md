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

Staging and smoke checks (require the local pinned checkout from `bootstrap_sdk.py`):

```text
python math/tools/bootstrap_sdk.py
python math/tools/smoke_sdk_game.py          # config-level: 16 event mappings, modes
python math/tools/smoke_sdk_state.py         # state-level: determinism + contract, 4 modes
python -m unittest math/tests/test_sdk_native.py   # SDK-native contract / replay tests
```

`bootstrap_sdk.py` stages the overlay into `games/black_market/` after revision validation. `smoke_sdk_game.py` instantiates `GameConfig` inside the staged checkout and asserts the configuration, all Bonus Buy modes, and the complete frontend event mapping. `smoke_sdk_state.py` and `test_sdk_native.py` drive the staged `GameState` directly and assert deterministic replay (same seed → same book), the typed 16-event contract with monotonic indices and integer-hundredth amounts, wallet↔book coherence (including wincap caps), and Free Spins / Hold & Spin sequencing.

## SDK-native pipeline

The official Stake Engine pipeline runs end-to-end against the staged game from
the SDK root (cwd matters — `execute_all_tests` resolves relative
`games/black_market/...` paths):

```text
cd math/.stake-engine/math-sdk
$env:PYTHONPATH="<absolute sdk root>"
python games/black_market/run.py
```

`run.py` executes the official stages in order: `create_books` (books, lookup tables, force files, verification sidecars), `generate_configs` (BE/FE/math configs + `index.json`), `create_stat_sheet` (PAR-style statistics + `statistics_summary.json` + `.xlsx`), and `execute_all_tests` (RTP/format/consistency checks). Simulation counts default to 25k / 10k / 10k / 10k and can be overridden via `BLM_{BASE,BACKROOM,VAULT,BLACK_CARD}_SIMS`. `run.py` first removes stale `lookUpTable_<mode>_0.csv` copies it would otherwise inherit (the SDK only recreates the `_0` file when it is missing), so the published LUT ids always match the freshly generated books.

Verify the published books against the frontend contract:

```text
python math/tools/verify_sdk_books.py
```

`verify_sdk_books.py` decompresses every `books_<mode>.jsonl.zst`, asserts that only the 16 contract event types appear, every payload key required by the contract is present, amounts are integer hundredths, and every round is coherent (exactly one `payout` + `roundEnd`; `roundEnd.payoutMultiplier` == `payout.amount` == `payout.total` == book `payoutMultiplier`; uncapped `baseGameWins` + `freeGameWins` ≥ the capped multiplier).

Record the per-mode replay IDs needed for staging validation:

```text
python math/tools/find_sdk_replays.py
```

`find_sdk_replays.py` scans the published books and writes `replay_manifest.json`
next to `publish_files/` with a `loss` / `low_win` / `mid_win` / `high_win` /
`max_win` book ID per mode (buy modes have no true loss by design — the closest
category records are listed instead). Re-run it after regenerating on the
approved production inputs so the IDs point at the shipped books.

The repository does **not** contain fabricated production math. Final RTP, hit rate, volatility, payout table, and max-win frequency must be produced and verified from the approved simulation set before submission.

## Provisional round simulator and publication pipeline

`math/black_market/simulator.py` implements a seeded provisional round generator that drives the phase-1 event contract (`GameExecutables` / `GameState`) to produce development-scale result books. Rules are documented as provisional and mirror the overlay values in `math/sdk_game/black_market/game_config.py` (must be kept in sync).

Mechanics implemented:
- Uniform random 5×4 board draw from the overlay reel CSV strips (base / free-spin / hold-and-spin decks)
- Pay-anywhere cluster detection: orthogonally connected groups ≥ 8 matching symbols with wild substitution, paid from the provisional paytable (bands: 8–9 / 10–11 / 12–14 / 15–20)
- Cascade loop with multiplier progression in free spins (1× → 2× → 3× → 5× → 10×, advancing per cascade)
- Free Spins: 3/4/5 scatters → 8/10/12 spins; retriggers during feature
- Expanding Wilds: full-reel expansion when a wild is part of a winning cluster
- Hold & Spin: ≥ 6 prize symbols trigger; respins reset on new lock; ends on 0 respins or full board
- Forced max-win book at the overlay `wincap` frequency (0.1% of base rounds)
- Buy modes: Back Room = forced Free Spins; Vault = forced Hold & Spin; Black Card = Free Spins + Hold & Spin with a boosted starting multiplier

Run the provisioner at development scale (100k rounds per mode):

```text
python math/tools/build_provisional_package.py --rounds 100000
```

Output is written to `math/.artifacts/provisional-package/` (Git-ignored) and includes per-mode compressed books (`.jsonl.zst`), lookup CSVs, `index.json`, `provisional-summary.json` with PAR-style statistics, and a replay manifest with IDs for loss / low / mid / high / max wins per mode. Every artifact is explicitly labeled PROVISIONAL.

Validate a generated package:

```text
python math/tools/validate_delivery.py --package math/.artifacts/provisional-package
```

All provisional RTP values in the package are **unoptimized and off-target**; they are pipeline proofs, not approved math. Replace with the certified simulation set before submission.

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
python math/tools/smoke_sdk_game.py
python math/tools/smoke_sdk_state.py
python -m unittest math/tests/test_sdk_native.py
python math/tools/verify_sdk_books.py
python math/tools/validate_delivery.py --package <artifact-directory>
```

The simulator tests exercise seeded determinism, contract compliance, forced-feature mode event coverage, and paytable band accuracy across all four bet modes. The SDK-native tests exercise the staged `GameState` inside the pinned checkout: round contract across all mode/criteria buckets, deterministic replay, Free Spins multiplier progression, Hold & Spin locked totals, and wallet↔book accumulation. The delivery validator cross-checks every book/LUT pay offset and every `index.json` entry against its compressed result; `verify_sdk_books.py` checks the generated Engine books against the frontend event contract. Generated SDK checkouts and math artifacts are ignored by Git.
