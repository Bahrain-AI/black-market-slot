BLACK MARKET — SDK-native math game (PROVISIONAL)
=================================================

Board      5 reels x 4 rows, pay-anywhere CLUSTERS (8+ connected), cascades.
Symbols    H1-H4, L1-L4 (pays) | W wild (expanding) | S scatter | P prize.
Free Spins 3+ S -> 8/10/12 spins; multiplier progression 1/2/3/5/10 (win step).
Hold&Spin  Buy-only bonus (P prizes; respin resets on each lock).
Bet Modes  base (1.0) | backroom (60, buy FS) | vault (100, buy H&S) |
           black_card (200, buy FS + H&S). Wincap 5000.

RUN
---
    python games/black_market/run.py

Optional env overrides: BLM_BASE_SIMS / BLM_BACKROOM_SIMS / BLM_VAULT_SIMS /
BLM_BLACK_CARD_SIMS (defaults: 25k / 10k / 10k / 10k).

OUTPUT (games/black_market/library/)
    books/            temporary thread books (JSON lines; zstd compressed).
    lookup_tables/    base lookup tables & segmented pay-splits.
    forces/           force-record lookups per mode.
    configs/          fe/be/math/index configs + event_config files.
    publish_files/    books_<mode>.jsonl.zst + lookUpTable_<mode>_0.csv (RGS set).

INFO
----
* ALL parameters here are PROVISIONAL phase-1 placeholders. They are NOT
  approved production math and MUST NOT be submitted to the ACP.
* Event emission is restricted to the 16-event frontend contract documented
  in math/sdk_game/black_market/game_events.py (books replay in the game's
  EventPlayer without mapping).
* The sanctioned Optimizer round (Rust, `run_optimization=True`) is disabled
  in this environment; it must run with approved paytable/reels before the
  published RGS set is completed.