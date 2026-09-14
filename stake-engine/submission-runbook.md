# BLACK MARKET — Stake Engine submission runbook

This runbook is the step-by-step process for officially submitting BLACK MARKET
on the Stake Engine Admin Control Panel (ACP) portal. It distinguishes what this
repository already produces from what still requires external inputs (approved
math, asset licensing, and your ACP/staging credentials).

> ⚠️ **Critical gate:** BLACK MARKET must **not** be submitted while the math
> package is provisional. The Engine rejects — and approval review will reject —
> games whose rules/RTP do not exactly match the published math package. The
> provisional package generated here is for pipeline validation only.

---

## 1. What already exists in this repository

| Item | Location | Status |
| --- | --- | --- |
| Frontend build | `dist/` (via `pnpm build`) | Ready — static-only, no external CDNs |
| SDK-native game overlay | `math/sdk_game/black_market/` → staged as `math/.stake-engine/math-sdk/games/black_market/` | Ready, provisional inputs |
| SDK-native pipeline run | Official `create_books` → `generate_configs` → `create_stat_sheet` → `execute_all_tests` runs end-to-end (25k/10k/10k/10k validated) | Ready (stage 2 re-runs on approved inputs) |
| Book/tooling verification | `math/tools/verify_sdk_books.py`, `math/tools/smoke_sdk_state.py`, `math/tests/test_sdk_native.py`, `math/tools/smoke_sdk_game.py` | Green
| Provisional package builder | `math/tools/build_provisional_package.py` | Ready — dev-scale, PROVISIONAL only |
| Tile package | `stake-engine/tile-package/` | Ready (placeholder art, within 3 MB) |
| Game copy / metadata | `stake-engine/game-description.md`, `stake-engine/submission-metadata.json` | Ready |
| Rules UI (config-driven) | `src/game/config/rules.ts` + `src/App.svelte` | Ready, provisional values |
| Submission status | `stake-engine/submission-checklist.md` | Tracked here |

## 2. External inputs required before submission

These are deliberately **not** fabricated in this repository:

1. **Approved production math inputs** — final paytable, reel strips, and
   probability distributions reviewed and signed off (PAR).
2. **Certified simulation set** — 100k+ diverse simulations per production
   mode on the approved inputs.
3. **Optimized lookup tables** — weighted to the final RTP (± tolerances below).
4. **Final PAR / statistics review** — RTP 90–98%, ±0.5% between modes,
   max-win frequency per Engine acceptance criteria.
5. **Replay event IDs** for loss, normal win, big win and max win per mode,
   recorded from the final books.
6. **Asset licensing confirmation** — ownership/licensing of every final
   visual and audio asset.
7. **ACP/staging credentials** — your account access to the portal.

## 3. Regenerate the math package on approved inputs

When approved inputs exist, run the official Stake Math SDK workflow (see the
`stake-math-sdk` skill) against the pinned checkout to produce the publish
artifacts **for every mode**. The repository-owned overlay under
`math/sdk_game/black_market/` already implements the complete SDK-native game;
replacing the provisional inputs in `game_config.py` (paytable, reels,
distributions) is the only change the approved-input round needs. Run the SDK
pipeline from the SDK root — `execute_all_tests` resolves relative
`games/black_market/...` paths from the current directory:

```
cd math/.stake-engine/math-sdk
$env:PYTHONPATH="<absolute sdk root>"     # PowerShell; export PYTHONPATH on POSIX
python games/black_market/run.py
```

`run.py` produces per-mode result books, weighted lookup tables (`_0.csv`),
`index.json`, BE/FE/math configs, a PAR-style statistic sheet, and runs the
Engine's own format/RTP checks. Simulation counts can be overridden with
`BLM_{BASE,BACKROOM,VAULT,BLACK_CARD}_SIMS` (defaults 25k/10k/10k/10k).

Verify the generated package before upload:

```
python math/tools/verify_sdk_books.py                    # book event contract
python math/tools/validate_delivery.py --package <approved-output>   # cross-file checks
python math/tools/smoke_sdk_state.py                     # determinism + contract smoke
python math/tools/find_sdk_replays.py                    # replay IDs per mode -> replay_manifest.json
```

`find_sdk_replays.py` writes `replay_manifest.json` beside `publish_files/` with
the book ID per mode for `loss` / `low_win` / `mid_win` / `high_win` / `max_win`
— the IDs to use for the `replay=true&event=<mode>/<id>` staging checks in §6.
Regenerate it with the approved production books; buy modes have no true loss by
design, so the closest category record (lowest payout) is listed for them.

Until approved inputs are available, run the provisional builders only to prove
the pipeline:

```
python math/tools/build_provisional_package.py --rounds 100000
# -> math/.artifacts/provisional-package/  (PROVISIONAL, never submittable)
```

## 4. PAR / statistics acceptance criteria

The final review must show, per production mode:

- RTP within **90–98%**
- RTP spread between modes within **±0.5%**
- Max-win frequency within Stake Engine guidelines
- Hit rate, volatility and feature frequencies consistent with the rules text

The rules/paytable shown in the UI must exactly match this published math.

## 5. Prepare the portal submission

### 5.1 Frontend
```
nvm use
npm i -g pnpm@10.5.0   # or corepack pnpm
pnpm install
pnpm build
```
Upload the entire `dist/` directory as the Front End build. `index.html` uses a
relative base (`./`) and reaches the RGS only through the launch-time `rgs_url`.

### 5.2 Tile package
Use `stake-engine/tile-package/` (regenerate with:
`python tools/submission/build_tile_package.py`). Combined size ≤ 3 MB is
enforced by the script. Replace with final approved artwork before submission.

### 5.3 Game information in the portal
Enter from `stake-engine/submission-metadata.json` and `game-description.md`:
name, provider (GRIND. / Grind Studios), category (Slots), theme tags,
description, RTP, max win, bet modes and costs. Set final values only once the
approved math package exists.

## 6. Staging validation checklist (ACP)

Once the package is uploaded to staging:

- [ ] Game loads from the launch URL with `sessionID`, `lang`, `device`, `rgs_url`.
- [ ] `/wallet/authenticate` populates balance, currency, min/max/step and all
      bet levels.
- [ ] Base round plays and pays exactly as recorded in the published book.
- [ ] Replays work: `replay=true&event=<mode>/<id>` renders loss, normal win,
      big win and max win for **every** mode without any wallet calls.
- [ ] Buy Bonus modes (Back Room / Vault / Black Card) enter their feature at the
      published cost and pay as recorded.
- [ ] Win increment animation matches the published `payoutMultiplier` for
      every multi-event result.
- [ ] All declared languages render correctly.
- [ ] All declared currencies format and settle correctly.
- [ ] Desktop, mobile, and small popout layouts pass review.
- [ ] Browser network console is clean during review (no failed requests,
      no external origins).
- [ ] Min/max bet enforcement and spacebar=spin behave per jurisdiction config.
- [ ] Turbo disabled where the jurisdiction config requires it.

## 7. Live validation and approval

- Confirm final RTP/max win displayed in-game match the approved math.
- Run live rounds in each mode and cross-check payouts against the books.
- After approval, publish per the Engine portal workflow.

## 8. Current blocker summary

Everything in §5 is ready except the approval-gated items: approved math
inputs, certified simulation set, optimized lookup tables, PAR review, replay
records from final books, asset licensing confirmation, and ACP credentials.

**Do not submit until §2 and §3 are complete.**