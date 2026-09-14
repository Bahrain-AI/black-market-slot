"""In-checkout state-level smoke for the SDK-native BLACK MARKET game.

Run by ``tools/smoke_sdk_state.py`` with cwd = games/black_market and
PYTHONPATH = game_root;sdk_root;math_root.  Exercises every bet mode/criteria
against the real SDK run flow (run_spin -> cluster wins -> tumble -> FS ->
Hold & Spin -> round end) and asserts the 16-event book contract, the
hundredths amount convention, criteria-specific feature expectations, Hold &
Spin sequencing, and full determinism (same seed -> identical book).

Exit code 0 with a JSON report on success.
"""

import json

from black_market.sdk import FRONTEND_CONTRACT

from game_config import GameConfig
from gamestate import GameState
import game_events as ev

VALID = ev.VALID_EVENT_TYPES
MAX_WIN = 5000
PROGRESSION = [1, 2, 3, 5, 10]

MODES = [
    ("base", "wincap"),
    ("base", "freegame"),
    ("base", "0"),
    ("base", "basegame"),
    ("backroom", "freegame"),
    ("vault", "holdspin"),
    ("black_card", "hybrid"),
]

N_ROUNDS = 40
SEEDS = list(range(2000, 2000 + 6))  # determinism sample


def _check_round(gs, mode, criteria, errors, stats, sim):
    """Run one round and validate every contract invariant."""
    gs.run_spin(sim, 3000 + sim)
    book = gs.book
    book_json = book.to_json()
    events = book.events
    stats["rounds"] += 1
    stats["events"] += len(events)

    types = [e["type"] for e in events]
    if not types:
        errors.append("empty book")
        return
    for t in types:
        if t not in VALID:
            errors.append(f"event type outside contract: {t}")

    counts = {}
    for idx, e in enumerate(events):
        t = e["type"]
        counts[t] = counts.get(t, 0) + 1
        if e.get("index") != idx:
            errors.append(f"{t}: index {e.get('index')} != position {idx}")
        missing = [k for k in FRONTEND_CONTRACT[t] if k not in e]
        if missing:
            errors.append(f"{t}: missing payload keys {missing}")
        if t == "win" and not isinstance(e["amount"], int):
            errors.append("win.amount not int hundredths")
        if t == "cascade" and not isinstance(e["cascade"], int):
            errors.append("cascade not int")
        if t == "freeSpin":
            if not (isinstance(e["current"], int) and isinstance(e["total"], int)):
                errors.append("freeSpin fields not int")
            if e["remaining"] != max(0, e["total"] - e["current"]):
                errors.append("freeSpin.remaining mismatch")
        if t == "multiplierIncrease":
            if not (e["from"] in PROGRESSION and e["to"] in PROGRESSION):
                errors.append(f"multiplierIncrease outside progression: {e['from']}->{e['to']}")
            if e["from"] >= e["to"]:
                errors.append("multiplierIncrease not increasing")
        if t in ("holdSpinRespins",):
            if not (isinstance(e["remaining"], int) and 0 <= e["remaining"] <= gs.config.holdspin_respins):
                errors.append(f"holdSpinRespins out of range: {e['remaining']}")
        if t == "expandWild" or t == "expandingWild":
            if not isinstance(e["reel"], int):
                errors.append("expandingWild.reel not int")
            if e["rows"] != list(range(gs.config.num_rows[e["reel"]])):
                errors.append("expandingWild.rows not full reel")
        if t in ("reveal", "collapse", "refill"):
            board = e["board"]
            if len(board) != gs.config.num_reels or any(len(r) != gs.config.num_rows[0] for r in board):
                errors.append(f"{t}: board shape mismatch")
            for reel in board:
                for cell in reel:
                    if "name" not in cell:
                        errors.append(f"{t}: cell missing name")
        if t == "payout":
            if not (isinstance(e["amount"], int) and isinstance(e["total"], int)):
                errors.append("payout fields not int")
            if e["amount"] != e["total"]:
                errors.append(f"payout amount {e['amount']} != total {e['total']}")
        if t == "holdSpinLock":
            for lock in e["locks"]:
                if not isinstance(lock.get("value"), int):
                    errors.append("holdSpinLock value not int")
        if t == "holdSpinStart":
            for lock in e["locked"]:
                if not isinstance(lock.get("value"), int):
                    errors.append("holdSpinStart locked value not int")

    # Cascade numbering within the round must restart per round and increase.
    if "cascade" in counts:
        cascade = [e["cascade"] for e in events if e["type"] == "cascade"]
        if cascade != list(range(1, len(cascade) + 1)):
            errors.append(f"cascade numbering broken: {cascade}")

    round_end = [e for e in events if e["type"] == "roundEnd"]
    payout = [e for e in events if e["type"] == "payout"]
    if len(round_end) != 1 or len(payout) != 1:
        errors.append("round must contain exactly one payout and one roundEnd")
        return

    pm = round_end[0]["payoutMultiplier"]
    if pm != payout[0]["amount"]:
        errors.append(f"roundEnd {pm} != payout.amount {payout[0]['amount']}")
    if pm != book_json["payoutMultiplier"]:
        errors.append(f"roundEnd {pm} != book.payoutMultiplier {book_json['payoutMultiplier']}")
    if not isinstance(pm, int):
        errors.append("roundEnd.payoutMultiplier not int hundredths")
    if abs((book_json["baseGameWins"] + book_json["freeGameWins"]) - (pm / 100.0)) > 1e-6:
        errors.append("book base+free != payoutMultiplier")

    final = pm / 100.0
    stats["payout"] += final

    fs_count = counts.get("freeSpinsStart", 0)
    hs_count = counts.get("holdSpinStart", 0)

    # Criteria-specific feature expectations.
    if criteria == "0" and final != 0:
        errors.append(f"'0' criteria won {final}")
    if criteria == "basegame" and (final <= 0 or fs_count):
        errors.append(f"basegame criteria: final={final}, fs={fs_count}")
    if criteria in ("freegame", "wincap") and mode == "base" and not fs_count:
        errors.append(f"{criteria} criteria missing freespins")
    if criteria == "wincap" and final != MAX_WIN:
        errors.append(f"wincap criteria final {final} != {MAX_WIN}")
    if mode == "backroom":
        if not fs_count or hs_count:
            errors.append("backroom must play free spins only")
    if mode == "vault":
        if not hs_count or counts.get("freeSpinsStart", 0):
            errors.append("vault must play hold & spin only")
    if mode == "black_card":
        if not (fs_count and hs_count):
            errors.append("black_card must play free spins + hold & spin")

    # Free spin sequencing.
    fs_events = [e for e in events if e["type"] == "freeSpin"]
    starts = [e for e in events if e["type"] == "freeSpinsStart"]
    if fs_events:
        currents = [e["current"] for e in fs_events]
        if currents != list(range(1, len(currents) + 1)):
            errors.append(f"freeSpin current sequence broken: {currents[:6]}...")
        totals = {e["total"] for e in starts + fs_events}
        if len(totals) != 1:
            pass  # retriggers legitimately extend totals mid-session

    # Hold & Spin sequencing: emitted remaining is the post-decrement value,
    # so each step is either -1 of the previous or a full reset to R-1.
    respins = [e["remaining"] for e in events if e["type"] == "holdSpinRespins"]
    if len(respins) > 1:
        r_max = gs.config.holdspin_respins - 1
        for i in range(1, len(respins)):
            down = respins[i] == respins[i - 1] - 1
            reset_after_lock = respins[i] == r_max
            if not (down or reset_after_lock):
                errors.append(f"holdSpinRespins sequence broken: {respins[:10]}")
    for r in respins:
        if not (isinstance(r, int) and 0 <= r <= gs.config.holdspin_respins - 1):
            errors.append(f"holdSpinRespins out of range: {r}")
    if hs_count:
        he = [e for e in events if e["type"] == "holdSpinEnd"]
        if len(he) != 1:
            errors.append("hold & spin round missing holdSpinEnd")
        else:
            locked_total = sum(
                l["value"] for l in [e for e in events if e["type"] == "holdSpinStart"][0]["locked"]
            )
            for lock_e in [e for e in events if e["type"] == "holdSpinLock"]:
                locked_total += sum(l["value"] for l in lock_e["locks"])
            if he[0]["total"] != locked_total:
                errors.append(f"holdSpinEnd {he[0]['total']} != locked total {locked_total}")


def main():
    config = GameConfig()
    gs = GameState(config)

    report = {"modes": [], "errors": 0, "deterministic": True, "mismatch": []}
    for mode, criteria in MODES:
        gs.betmode = mode
        gs.criteria = criteria
        errors = []
        stats = {"rounds": 0, "events": 0, "payout": 0.0}
        for sim in range(N_ROUNDS):
            _check_round(gs, mode, criteria, errors, stats, sim)
        entry = {
            "mode": mode,
            "criteria": criteria,
            "rounds": stats["rounds"],
            "events": stats["events"],
            "provisionalAvgPayout": round(stats["payout"] / max(stats["rounds"], 1), 4),
            "errors": len(errors),
            "sampleErrors": errors[:8],
        }
        report["modes"].append(entry)
        report["errors"] += len(errors)

    # Determinism: fresh gamestate, same seeds -> identical books.
    gs2 = GameState(config)
    for mode, criteria in MODES:
        for seed in SEEDS:
            gs.betmode = mode
            gs.criteria = criteria
            gs.run_spin(seed, seed)
            a = json.dumps(gs.book.events, sort_keys=True) + "|" + str(gs.book.payout_multiplier)
            gs2.betmode = mode
            gs2.criteria = criteria
            gs2.run_spin(seed, seed)
            b = json.dumps(gs2.book.events, sort_keys=True) + "|" + str(gs2.book.payout_multiplier)
            if a != b:
                report["deterministic"] = False
                report["mismatch"].append(f"{mode}/{criteria} seed {seed}")
    report["determinismSeeds"] = SEEDS

    print(json.dumps(report, indent=2))
    return 1 if (report["errors"] or not report["deterministic"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())