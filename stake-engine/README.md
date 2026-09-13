# Stake Engine integration

This repository is structured as a static Svelte 5 + Vite frontend that can be uploaded to Stake Engine after `pnpm build`. The build uses `base: './'` and contains no runtime dependency on external CDNs.

## Engine runtime flow

1. Read `sessionID`, `lang`, `device`, and `rgs_url` from the launch URL.
2. Call `POST {rgs_url}/wallet/authenticate` once on normal game load.
3. Populate balance, currency, min/max/step and all selectable bet levels from the authentication response.
4. Place a round using `POST {rgs_url}/wallet/play` with `{ sessionID, amount, mode }`.
5. Render only the events returned by the RGS for production rounds.
6. Complete the round with `POST {rgs_url}/wallet/end-round` where required by the published math configuration.

Replay mode is detected with `replay=true`. It makes no authenticated wallet calls and loads the published result from `GET {rgs_url}/bet/replay/{game}/{version}/{mode}/{event}`.

## Build

```bash
nvm use
npm i -g pnpm@10.5.0
pnpm install
pnpm build
```

Upload the entire `dist/` directory as the Front End build in Engine.

## Important production gate

The frontend integration is prepared, but the game must **not** be submitted for approval until the final math package exists and the rules/paytable shown in the UI exactly match that published math. Stake Engine requires an `index.json`, a weighted CSV lookup table, and a Zstandard-compressed JSONL result book for every mode.
