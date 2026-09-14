"""Stage and smoke-test the BLACK MARKET official SDK game configuration."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

MATH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MATH_ROOT))

from black_market.sdk import stage_sdk_game

# Payload keys the frontend deterministic event contract requires per event type
# (mirrors src/game/events/types.ts; every key must be present).
FRONTEND_CONTRACT: dict[str, list[str]] = {
    "reveal": ["board"],
    "win": ["positions", "amount", "symbol"],
    "cascade": ["cascade"],
    "removeSymbols": ["positions"],
    "collapse": ["board"],
    "refill": ["board", "positions"],
    "expandingWild": ["reel", "rows"],
    "freeSpinsStart": ["total", "multiplier"],
    "freeSpin": ["current", "total", "remaining"],
    "multiplierIncrease": ["from", "to", "reason"],
    "holdSpinStart": ["respins", "locked"],
    "holdSpinLock": ["locks", "resetRespins"],
    "holdSpinRespins": ["remaining"],
    "holdSpinEnd": ["total"],
    "payout": ["amount", "total"],
    "roundEnd": ["payoutMultiplier"],
}


def _check_program() -> str:
    """Return the JSON printed by the in-checkout smoke program."""
    return """
import json
from game_config import GameConfig
import game_events

c = GameConfig()
assert c.num_reels == 5 and c.num_rows == [4] * 5
assert c.rtp == 0.96 and c.provisional is True
assert c.multiplier_progression == [1, 2, 3, 5, 10]
assert c.wincap == 5000.0
assert set(c.reels) == {"BR0", "FR0", "HR0"}
assert set(c.special_symbols["wild"]) == {"W"}
assert set(c.special_symbols["scatter"]) == {"S"}
assert set(c.special_symbols["prize"]) == {"P"}

mode_names = [m.get_name() for m in c.bet_modes]
expected = {"base": (1.0, False), "backroom": (60.0, True), "vault": (100.0, True), "black_card": (200.0, True)}
assert set(mode_names) == set(expected), mode_names
for mode in c.bet_modes:
    cost, buy_bonus = expected[mode.get_name()]
    assert mode.get_cost() == cost, (mode.get_name(), mode.get_cost())
    assert mode.get_buybonus() is buy_bonus, (mode.get_name(), mode.get_buybonus())
    assert mode.get_wincap() == c.wincap
assert sum(mode.get_cost() * d.get_quota() for mode in c.bet_modes for d in mode.get_distributions()) > 0

# Emit every mapped event through an SDK-shaped book to prove the output contract.
class Book:
    def __init__(self):
        self.events = []
    def add_event(self, event):
        self.events.append(event)

class Gamestate:
    def __init__(self):
        self.book = Book()

g = Gamestate()
events = [
    ("reveal", lambda: game_events.reveal(g, [["H1"] * 4] * 5)),
    ("win", lambda: game_events.win(g, [{"reel": 0, "row": 0}], 100, "H2")),
    ("cascade", lambda: game_events.cascade(g, 2)),
    ("removeSymbols", lambda: game_events.remove_symbols(g, [{"reel": 0, "row": 0}])),
    ("collapse", lambda: game_events.collapse(g, [["H1"] * 4] * 5)),
    ("refill", lambda: game_events.refill(g, [["H1"] * 4] * 5, [{"reel": 4, "row": 3}])),
    ("expandingWild", lambda: game_events.expanding_wild(g, 2, [0, 1, 2, 3])),
    ("freeSpinsStart", lambda: game_events.free_spins_start(g, 8, 1)),
    ("freeSpin", lambda: game_events.free_spin(g, 1, 8)),
    ("multiplierIncrease", lambda: game_events.multiplier_increase(g, 1, 2, "cascade")),
    ("holdSpinStart", lambda: game_events.hold_spin_start(g, 3, [{"reel": 0, "row": 0, "value": 1}])),
    ("holdSpinLock", lambda: game_events.hold_spin_lock(g, [{"reel": 4, "row": 3, "value": 5}], False)),
    ("holdSpinRespins", lambda: game_events.hold_spin_respins(g, 2)),
    ("holdSpinEnd", lambda: game_events.hold_spin_end(g, 10)),
    ("payout", lambda: game_events.payout(g, 250, 250)),
    ("roundEnd", lambda: game_events.round_end(g, 250)),
]
FRONTEND_CONTRACT = %s
for index, (event_type, emit) in enumerate(events):
    emitted = emit()
    assert emitted["index"] == index == g.book.events[index]["index"], emitted
    assert emitted["type"] == event_type, emitted
    missing = [key for key in FRONTEND_CONTRACT[event_type] if key not in emitted]
    assert not missing, (event_type, missing)

print(json.dumps({
    "gameId": c.game_id,
    "modes": [m.get_name() for m in c.bet_modes],
    "board": [c.num_reels, c.num_rows[0]],
    "targetRtp": c.rtp,
    "maxWin": c.wincap,
    "provisional": c.provisional,
    "reels": sorted(c.reels),
    "mappedEvents": len(g.book.events),
}))
""" % (
        json.dumps(FRONTEND_CONTRACT, sort_keys=True)
    )


def smoke(sdk_root: Path) -> dict[str, object]:
    staged = stage_sdk_game(sdk_root)
    game_root = Path(staged["target"])
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(sdk_root.resolve())
    result = subprocess.run(
        [sys.executable, "-c", _check_program()],
        cwd=game_root,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "sdk_root",
        nargs="?",
        type=Path,
        default=MATH_ROOT / ".stake-engine" / "math-sdk",
    )
    args = parser.parse_args()
    print(json.dumps(smoke(args.sdk_root), indent=2))