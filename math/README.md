# BLACK MARKET math

Stake Engine requires pre-generated, stateless outcomes. Production math should be generated with the official `StakeEngine/math-sdk` (recommended) or another generator that emits the exact Engine publication format.

## Target design

- Mode: `base`
- Cost multiplier: `1.0`
- Target RTP: `0.96` (96.00%)
- Target max win: `5000x`
- Board: 5 reels × 4 rows
- Stateless rounds only

The current repository does **not** contain fabricated production math. This is intentional: final RTP, hit rate, volatility, payout table, and max-win frequency must be produced and verified from the real simulation set before submission.

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

Each JSONL result must contain `id`, `events`, and `payoutMultiplier`. Lookup rows must contain unsigned integer values in the order `simulation_id,weight,payout_multiplier`, and the payout multiplier must exactly match the corresponding book result.

Engine recommends 100k+ production simulations per mode to create sufficient outcome diversity before optimization. Generate PAR/statistical output and verify RTP and max-win frequency before uploading math to ACP.
