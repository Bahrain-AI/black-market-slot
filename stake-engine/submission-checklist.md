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
- [ ] Final rules/paytable populated from approved math values.
- [ ] Verify exact win increment animation against every multi-event result.
- [ ] Validate all currencies/languages in Engine staging.
- [ ] Browser network/console must be clean during review.

## Math
- [ ] Final game logic implemented with Stake Engine Math SDK or equivalent compatible generator.
- [ ] 100k+ diverse simulations generated for each production mode (recommended by Engine docs).
- [ ] Weighted lookup tables optimized to final RTP.
- [ ] `payoutMultiplier` values match exactly between result books and lookup tables.
- [ ] `index.json` references every mode, cost, event book, and weight file.
- [ ] Result books are `.jsonl.zst`.
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
