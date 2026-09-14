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
- [ ] Final rules/paytable populated from approved math values.
- [ ] Verify exact win increment animation against every multi-event result.
- [ ] Validate all currencies/languages in Engine staging.
- [ ] Browser network/console must be clean during review.

## Math
- [x] Phase 1 5×4 configuration and event contract scaffold exists under `math/black_market/`.
- [x] Phase 1 deterministic helpers cover cascades, expanding Wilds, progressive multiplier state, and persistent Hold & Spin locks.
- [x] Validated uncompressed JSONL, lookup CSV, `index.json`, and `.jsonl.zst` generation hooks exist.
- [x] Official Stake Engine Math SDK checkout is pinned to commit `307e6812b38489e212f835001f21e9f7d4c18a4d`; bootstrap validates the revision and required SDK interfaces.
- [ ] Final game logic implemented with Stake Engine Math SDK or equivalent compatible generator.
- [ ] 100k+ diverse simulations generated for each production mode (recommended by Engine docs).
- [ ] Weighted lookup tables optimized to final RTP.
- [x] Local artifact validator checks exact `payoutMultiplier` matches between every result book and lookup row.
- [x] Local artifact validator checks every `index.json` mode, cost, event book, and weight file reference.
- [x] Zstandard compression and decompression integrity are covered by automated tests.
- [ ] Final production result books are generated as `.jsonl.zst`.
- [ ] PAR / statistics review completed: RTP, hit rate, volatility, max-win frequency.
- [ ] Replay event IDs recorded for loss, normal win, big win and max win for every mode.

## Product / compliance
- [x] Game is stateless: no jackpot, gamble, continuation, or early-cashout mechanic.
- [x] No Stake branding in game artwork.
- [x] No child-like characters or youth-targeted content.
- [x] Original visual direction.
- [ ] Confirm ownership/licensing of every final visual/audio asset.
- [ ] Add final game description / promotional blurb.
- [ ] Add final RTP and max win to in-game rules.

## Tile package
Stake Engine requires:
- [ ] `BlackMarket-BG.png` or `.jpg` — high-resolution environmental background.
- [ ] `BlackMarket-FG.png` — transparent foreground character/key item.
- [ ] `<ProviderName>-Logo.png` — transparent provider/studio logo.
- [ ] Background + foreground combined size <= 3 MB.

Do not submit until every unchecked approval-critical item above is complete.
