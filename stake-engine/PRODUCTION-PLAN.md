# BLACK MARKET Stake Engine ACP Production Plan
Read-only verification found a clean main branch at c87e0bef4f449f515396cfd8b5a28711464cdd66, matching origin/main. Build mode must save this plan as stake-engine/PRODUCTION-PLAN.md before implementation.
Confirmed decisions:
- Approved production math: unavailable.
- Reference-image rights: confirmed.
- Final art: replace current placeholders before submission.
- Languages: English only for the first submission.
- ACP access: unavailable.
- Execution: approved for every unblocked step.
Engine requires indexed events, compressed JSONL books, matching unsigned-integer LUT payouts, mandatory replay support, static frontend files, and RGS-controlled wallet operations. [Events](https://stake-engine.com/docs/math/game-state-structure/events), [math format](https://stake-engine.com/docs/math/math-file-format), [replay requirements](https://stake-engine.com/docs/approval-guidelines/game-replay-requirements), [RGS requirements](https://stake-engine.com/docs/approval-guidelines/rgs-communication).
Run before reading or changing tracked files:
```powershell
$Repo = 'C:\Users\ops8\.codex\.chatgpt-projects\g-p-6aa69668be808191b310d09c3c5e208d\black-market-slot'
Set-Location -LiteralPath $Repo

git fetch origin
git checkout main
git pull --ff-only origin main

if (@(git status --porcelain).Count -ne 0) {
    throw 'Working tree is not clean.'
}

$LocalHead = git rev-parse HEAD
$RemoteHead = ((git ls-remote origin refs/heads/main) -split '\s+')[0]
if ($LocalHead -ne $RemoteHead) {
    throw "Local main $LocalHead does not match origin/main $RemoteHead."
}

nvm use 22.16.0
corepack enable
corepack prepare pnpm@10.5.0 --activate

if ((node --version) -ne 'v22.16.0') { throw 'Node 22.16.0 is required.' }
if ((pnpm --version) -ne '10.5.0') { throw 'pnpm 10.5.0 is required.' }

python -c "import sys; assert sys.version_info[:2] == (3, 12), sys.version"
python -m pip install -r math/requirements.txt
```
Write this plan to stake-engine/PRODUCTION-PLAN.md, update its gate status as work progresses, and commit it before implementation.
Work possible now:
1. Add math/approved-inputs/schema.json and math/tools/validate_approved_inputs.py.
2. Make math/sdk_game/black_market/run.py require a validated approval manifest before accepting BLM_PRODUCTION=1.
3. Add BLM_RUN_OPTIMIZATION=1 support; retain the current provisional path for development.
4. Add math/tools/validate_par.py to enforce:
   - RTP per mode between 0.90 and 0.98.
   - Maximum absolute mode-to-mode RTP spread of 0.005.
   - Approved maximum-win frequency bounds.
   - Approved hit-rate, volatility, and feature-frequency bounds.
5. Prevent release tooling from accepting any input or artifact marked provisional.
If approved inputs remain absent, stop here, retain provisional = True, and report G1 as BLOCKED-ON-USER. Do not run a provisional package and rename it as final.
When approved inputs arrive:
1. Store and hash the signed source package under math/approved-inputs/.
2. Replace provisional values in:
   - math/sdk_game/black_market/game_config.py
   - math/sdk_game/black_market/game_optimization.py
   - math/sdk_game/black_market/reels/*.csv
   - Other SDK game modules only if the approved mechanics differ.
3. Mirror final public values into math/black_market/game_config.py, src/game/config/rules.ts, and stake-engine/submission-metadata.json.
4. Set provisional false only after input validation succeeds.
5. Run the pinned SDK, at least 100,000 simulations for each of the four modes, and the Rust optimizer.
```powershell
Set-Location -LiteralPath $Repo

python math/tools/validate_approved_inputs.py --input math/approved-inputs
python math/tools/bootstrap_sdk.py
python math/tools/smoke_sdk_game.py
python math/tools/smoke_sdk_state.py
python -m unittest discover -s math/tests -v

$Sdk = (Resolve-Path 'math/.stake-engine/math-sdk').Path
$Publish = Join-Path $Sdk 'games\black_market\library\publish_files'
$Stats = Join-Path $Sdk 'games\black_market\library\statistics_summary.json'

if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    throw 'Rust/Cargo is required for final lookup optimization.'
}

cargo build --release --manifest-path (Join-Path $Sdk 'optimization_program\Cargo.toml')

$env:PYTHONPATH = $Sdk
$env:BLM_PRODUCTION = '1'
$env:BLM_RUN_OPTIMIZATION = '1'
$env:BLM_BASE_SIMS = '100000'
$env:BLM_BACKROOM_SIMS = '100000'
$env:BLM_VAULT_SIMS = '100000'
$env:BLM_BLACK_CARD_SIMS = '100000'

Push-Location $Sdk
try {
    python games/black_market/run.py
} finally {
    Pop-Location
}

python math/tools/verify_sdk_books.py $Publish
python math/tools/validate_delivery.py --package $Publish
python math/tools/validate_par.py --statistics $Stats --approval math/approved-inputs/approval.json
python math/tools/find_sdk_replays.py $Publish
```
Verification must prove:
- Only the 16 typed event names appear and all indices are monotonic.
- Event and book amounts remain integer hundredths.
- Every book ID and payoutMultiplier exactly matches its LUT row.
- Every mode has at least 100,000 diverse final records.
- Final RTP and spread pass the stated bounds.
- Maximum-win frequency and PAR metrics satisfy the supplied approval.
- Final .jsonl.zst files decompress and hash correctly.
- Replay IDs come from final books. Buy modes record the lowest-payout result as the documented loss substitute.
- Rules, metadata, mode costs, RTP, and maximum win match final math exactly.
G1 definition of done: approved-source hashes, final simulation outputs, optimized LUTs, PAR approval, final replay manifest, and frontend-rule parity are all recorded and green.
Work possible now:
1. Record the user’s confirmation that the supplied reference image is owned or licensed.
2. Add assets/PRODUCTION-LICENSES.json and a validator requiring one provenance entry and SHA-256 hash per shipped image or audio file.
3. Update the tile builder with a release mode that refuses prototype/reference sources.
4. Produce an exact replacement inventory from assets/specs/mechanics-assets.md.
Required final inputs replace:
- Ten runtime symbol WebPs under assets/symbols/.
- Seven animation frame sets under assets/anim-frames/, covering Wild expansion, Scatter, multiplier badge, Hold & Spin symbol/frame, cascade removal, and refill.
- Final background, foreground, provider logo, and tile sources.
- Any shipped audio, or an explicit declaration that the release contains no audio.
After those inputs arrive:
```powershell
Set-Location -LiteralPath $Repo

pnpm gen:animations
python tools/submission/validate_assets.py --manifest assets/PRODUCTION-LICENSES.json
python tools/submission/build_tile_package.py --output stake-engine/tile-package

pnpm test
pnpm typecheck
pnpm build
```
Visual verification must cover desktop, mobile, and small popout views, all animation states, transparency, frame alignment, readable values, and absence of reference-derived placeholder material. Confirm:
- BlackMarket-BG.png: 1280×720.
- BlackMarket-FG.png: 1280×720 with transparency.
- GrindStudios-Logo.png: approved transparent logo.
- Combined tile size does not exceed 3 MB.
- Every shipped asset has an ownership or licence record.
- No external runtime URL is introduced.
G2 definition of done: final artwork is supplied, validated, visually approved by the user, fully covered by provenance records, and the tile package passes the size and format checks.
Repository work possible now:
1. Correct the frontend payout-unit boundary:
   - Keep all event amounts and payoutMultiplier values as integer hundredths.
   - Calculate wallet display wins as bet × payoutHundredths ÷ 100.
   - Convert demo fixtures from raw multipliers to integer hundredths.
   - Add tests using the existing 610 and 6400 SDK fixtures to prevent 100× display errors.
2. Implement production Bonus Buy controls:
   - Add Backroom, Vault, and Black Card selection and confirmation.
   - Show the configured 60×, 100×, and 200× costs.
   - Pass the selected mode to /wallet/play.
   - Let RGS balances and returned books remain authoritative.
   - Keep demo outcomes isolated from production sessions.
3. Declare English only in submission metadata and use the English locale consistently.
4. Add a release-bundle builder that refuses:
   - Provisional math or metadata.
   - Missing G1/G2 approval manifests.
   - Missing or mismatched hashes.
   - Uncompressed books.
   - External runtime URLs.
5. Build and validate:
```powershell
Set-Location -LiteralPath $Repo

pnpm install --frozen-lockfile
pnpm test
pnpm typecheck
pnpm build

$OutcomeRng = rg -n 'Math\.random|crypto\.getRandomValues' src/game/engine src/game/state src/lib/rgs.ts
if ($LASTEXITCODE -eq 0) {
    $OutcomeRng
    throw 'Outcome-path frontend RNG detected.'
}
if ($LASTEXITCODE -ne 1) { throw 'RNG scan failed.' }

$ExternalUrls = rg -n 'https?://|fonts\.googleapis|@import\s+url' dist
if ($LASTEXITCODE -eq 0) {
    $ExternalUrls
    throw 'External runtime dependency detected.'
}
if ($LASTEXITCODE -ne 1) { throw 'External URL scan failed.' }
```
After G1 and G2 are done and ACP access exists:
```powershell
$Version = '<approved-math-version>'
$Sdk = (Resolve-Path 'math/.stake-engine/math-sdk').Path
$Publish = Join-Path $Sdk 'games\black_market\library\publish_files'

python tools/submission/build_submission_bundle.py `
    --version $Version `
    --frontend dist `
    --math $Publish `
    --tiles stake-engine/tile-package `
    --metadata stake-engine/submission-metadata.json

python tools/submission/validate_submission_bundle.py `
    --bundle "stake-engine/release/$Version"
```
Upload the immutable frontend, math, tile, and metadata bundles through the authenticated ACP browser session. Credentials or tokens must never be written to repository files, terminal output, or chat.
Staging must verify:
- Authentication, RGS bet levels, balance, currency, and jurisdiction fields.
- Base, Backroom, Vault, and Black Card play requests.
- Exact win increments and final payouts against book values.
- Interrupted-round restoration.
- Replay URLs using separate game, version, mode, and event parameters.
- Loss, low, mid, high, and maximum-win records; documented substitutes for buy-mode losses.
- English UI at every screen.
- Every declared currency and supplied jurisdiction test session.
- Desktop, mobile, and small popout layouts.
- Spacebar, min/max bet, Turbo restrictions, and sound control.
- No wallet calls during replay.
- Clean browser console and network log with no external origins.
G3 definition of done: every staging check has captured evidence and the submission is READY-FOR-USER. Production publication requires a final explicit user action after reviewing that evidence.
Provide:
- Signed approval/version identifier and approver/date.
- Final per-mode RTP targets and costs.
- Final maximum win and acceptable maximum-win frequency.
- Paytable and win thresholds.
- BR0, FR0, and HR0 reel strips.
- Base/Free Spins/Hold & Spin trigger probabilities.
- Wild expansion rules and probabilities.
- Free Spins awards, retriggers, and multiplier progression.
- Hold & Spin prize values, weights, starting locks, respins, reset rules, and upgrades.
- Distribution quotas, optimizer fences, hit-rate, volatility, and feature-frequency targets.
- PAR report or written approval criteria.
These land in math/approved-inputs/ and then replace the provisional SDK configuration, reel, and optimizer files.
Reference-image ownership is already confirmed, but the selected submission policy is to replace placeholders. Provide the production symbol set, seven animation source sets, tile artwork, provider logo, and any audio, with creator/licensor, licence grant, approval date, and source file for each item. These land under their runtime paths and assets/PRODUCTION-LICENSES.json.
Provide later:
- Access through an authenticated ACP browser session.
- Team/game/version identifiers.
- Staging launch URL.
- Test sessions for every declared currency and jurisdiction.
- Final currency list.
- Final go-live approval.
No ACP secret lands in the repository.
Order:
1. Complete sync, plan materialization, payout-unit correction, Bonus Buy UI, English-only metadata, and submission validators now.
2. Keep G1 blocked until approved math arrives.
3. Keep G2 blocked until replacement art and licensing records arrive.
4. Close G1, then synchronize rules and metadata.
5. Close G2 and rebuild frontend/tile artifacts.
6. Assemble the immutable release bundle.
7. Upload and test staging only when G1 and G2 are done.
8. Stop at READY-FOR-USER before production publication.
```markdown
# BLACK MARKET production status

Baseline commit: c87e0bef4f449f515396cfd8b5a28711464cdd66
Release version: pending
Date: 2026-09-14T18:32:14Z

## G1 — Math
Status: BLOCKED-ON-USER
Inputs received: None; approved production math remains unavailable.
Changes: Added approval-manifest schema and validator, PAR validator, production/optimizer guards, and provisional-artifact release rejection.
Verification: SDK smoke checks reported zero errors; 18 math tests passed; production runner rejected the absent approval manifest.
RTP by mode: Not run; final approved inputs are absent.
RTP spread: Not run; final approved inputs are absent.
Maximum-win frequency: Not run; approved bounds are absent.
Book/LUT/replay hashes: Not available; final books were not generated.
Blocker or next action: Provide the signed approval/version package, values, reel strips, probabilities, optimizer fences, and PAR bounds listed above.

## G2 — Assets/provenance
Status: DONE | BLOCKED-ON-USER | READY-FOR-USER
Inputs received:
Rights/provenance result:
Atlas validation:
Tile dimensions and combined size:
Visual QA:
Blocker or next action:

## G3 — ACP/staging
Status: DONE | BLOCKED-ON-USER | READY-FOR-USER
Frontend commit/build hash:
Submission bundle hash:
ACP upload status:
Staging matrix completed:
Replay records tested:
Console/network result:
Blocker or next action:

## Final disposition
Production publish executed: NO
Current decision: <blocked reason or READY-FOR-USER>
Exact user action required:
```
