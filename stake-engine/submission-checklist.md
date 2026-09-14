# Stake Engine submission checklist — BLACK MARKET

## Frontend
- [x] Static build output only (`dist/`).
- [x] Svelte 5 + Vite with relative asset base (`./`).
- [x] No external fonts, analytics, scripts, APIs, or CDNs.
- [x] Uses `rgs_url` from launch query; never hardcodes RGS host.
- [x] Calls `/wallet/authenticate` before normal play.
- [x] Uses balance/currency/bet levels returned by RGS.
- [x] Supports minimum and maximum supplied bet levels.
- [x] Spacebar maps to Spin.
- [x] Turbo can be disabled by jurisdiction config.
- [x] Sound control exists.
- [x] Replay mode disables wallet play and uses replay endpoint.
- [x] Responsive layout for desktop, mobile, and small popout view.
- [x] Production reels and symbols render through one PixiJS 8 Application mounted by Svelte 5.
- [x] Typed, deterministic playback covers reveal, cascades, expanding Wilds, Free Spins multiplier state, Hold & Spin locks, payout, and round end.
- [x] Production frontend contains no outcome RNG; local demo events are isolated fixtures.
- [x] Ordered event indices are validated before playback and state reducers reject non-monotonic events.
- [x] Frontend round-book parser acceptance tests (`src/game/engine/roundBook.test.ts`) consume verbatim SDK book payloads covering all 16 event types (base cascade, Free Spins multiplier advance, Hold & Spin incl. a new lock landing during respins); 15 frontend tests pass, `svelte-check` clean, production build green.
- [x] Rules / game-information modal is config-driven (`src/game/config/rules.ts`), rendering features, bet modes, provisional RTP and max win from a single source of truth.
- [ ] Final rules/paytable populated from approved math values.
- [ ] Verify exact win increment animation against every multi-event result.
- [ ] Validate all currencies/languages in Engine staging.
- [ ] Browser network/console must be clean during review.

## Math
- [x] Phase 1 5×4 configuration and event contract scaffold exists under `math/black_market/`.
- [x] Phase 1 deterministic helpers cover cascades, expanding Wilds, progressive multiplier state, and persistent Hold & Spin locks.
- [x] Validated uncompressed JSONL, lookup CSV, `index.json`, and `.jsonl.zst` generation hooks exist.
- [x] Official Stake Engine Math SDK checkout is pinned to commit `307e6812b38489e212f835001f21e9f7d4c18a4d`; bootstrap validates the revision and required SDK interfaces.
- [x] Provisional BLACK MARKET SDK game overlay (`math/sdk_game/black_market/`) stages into the pinned checkout as `games/black_market/`; configures 5×4 board, symbols, provisional reels, base/Free Spins/Hold & Spin mechanics, Bonus Buy modes, and max-win/RTP hooks.
- [x] SDK smoke test (`math/tools/smoke_sdk_game.py`) instantiates `GameConfig` against the pinned checkout and proves all 16 frontend event types map through an SDK-shaped book with valid indices and payloads.
- [x] Seeded provisional round simulator (`math/black_market/simulator.py`) implements pay-anywhere cluster detection, cascades, expanding Wilds, Free Spins with multiplier progression, Hold & Spin with locked prizes, and buy-mode features; exercised across 4 bet modes.
- [x] Provisional package builder (`math/tools/build_provisional_package.py`) produces books, LUTs, `index.json`, `.jsonl.zst`, PAR-style statistics and replay records per mode; validated end-to-end at 100k rounds.
- [x] Delivery validator (`math/tools/validate_delivery.py`) cross-checks a generated package against the Engine contract and reports validity.
- [x] SDK-native game (`math/sdk_game/black_market/`, 9 overlay files + reels) implements the full game in official SDK shape (game `Config`, `GameEvents`, `GameCalculations`, `GameExecutables`, `GameOverride`, `GameState`, optimization stub, `run.py`) — paytable, BR0/FR0/HR0 reel strips (S-only/scatter deck, P-only Hold & Spin deck), base/Free Spins/Hold & Spin distributions with `reel_weights`, and BetModes for all Bonus Buy modes.
- [x] Official SDK pipeline runs end-to-end on the staged overlay (`create_books` → `generate_configs` → `create_stat_sheet` → `execute_all_tests`) at full scale (25k base / 10k others) from the SDK root; `execute_all_tests` completes its format/consistency checks (SHA-256 + payout hashes OK) — RTP/volatility violations remain expected warnings for the provisional inputs.
- [x] State-level deterministic smoke (`math/tools/smoke_sdk_state.py`) proves same-seed → same-book replay and the typed 16-event contract with integer-hundredth amounts across all 7 mode/criteria buckets.
- [x] SDK-native unit tests (`math/tests/test_sdk_native.py`) run in-process: round contract, deterministic replay, Free Spins multiplier progression, Hold & Spin locked totals, and wallet↔book accumulation incl. wincap caps.
- [x] Published books verified against the frontend contract (`math/tools/verify_sdk_books.py`): only the 16 event types, required payload keys present, amounts int hundredths, one coherent `payout`+`roundEnd` per book matching `payoutMultiplier` (4.92M events across 4 modes, 0 errors).
- [ ] Final game logic implemented with approved production inputs in the SDK overlay (current overlay inputs remain explicitly provisional).
- [ ] 100k+ diverse simulations generated for each production mode (recommended by Engine docs).
- [ ] Weighted lookup tables optimized to final RTP.
- [x] Local artifact validator checks exact `payoutMultiplier` matches between every result book and lookup row.
- [x] Local artifact validator checks every `index.json` mode, cost, event book, and weight file reference.
- [x] Zstandard compression and decompression integrity are covered by automated tests.
- [ ] Final production result books are generated as `.jsonl.zst`.
- [ ] PAR / statistics review completed: RTP, hit rate, volatility, max-win frequency.
- [x] Replay event IDs recorded for loss, normal win, big win and max win for every mode (`math/tools/find_sdk_replays.py` writes `replay_manifest.json` next to the published books; buy modes have no true loss by design — closest category records listed). Regenerate on the approved production books.

## Product / compliance
- [x] Game is stateless: no jackpot, gamble, continuation, or early-cashout mechanic.
- [x] No Stake branding in game artwork.
- [x] No child-like characters or youth-targeted content.
- [x] Original visual direction.
- [ ] Confirm ownership/licensing of every final visual/audio asset.
- [x] Game description / promotional blurb exists (`stake-engine/game-description.md`).
- [ ] Add final RTP and max win to in-game rules (requires approved math values).

## Tile package
- [x] `BlackMarket-BG.png` generated (`stake-engine/tile-package/`), 1280×720.
- [x] `BlackMarket-FG.png` generated (transparent foreground, 1280×720).
- [x] `GrindStudios-Logo.png` generated (512×384).
- [x] Combined size verified ≤ 3 MB (actual: ~1.5 MB).
- [ ] Replace placeholder art with final approved artwork/asset licensing.

## Submission infrastructure
- [x] Submission metadata (`stake-engine/submission-metadata.json`) capturing game info, bet modes, provisional math, required inputs.
- [x] Submission runbook (`stake-engine/submission-runbook.md`) documenting the full ACP portal upload process, staging validation checklist, and PAR acceptance criteria.
- [x] README (`stake-engine/README.md`) documents the Engine runtime flow and build instructions.

Do not submit until every unchecked approval-critical item above is complete.