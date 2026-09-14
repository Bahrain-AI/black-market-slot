"""BLACK MARKET game events — emitted books use ONLY the frontend player contract.

The books produced by the SDK-native game contain exactly the sixteen event types
the frontend (``src/game/events/types.ts``) and the RGS replay player are built
around:

    reveal, win, cascade, removeSymbols, collapse, refill, expandingWild,
    freeSpinsStart, freeSpin, multiplierIncrease, holdSpinStart, holdSpinLock,
    holdSpinRespins, holdSpinEnd, payout, roundEnd

All amount/payout payloads follow the engine convention of hundredths
(payout-multiplier scaled by 100) so the books are directly RGS-verifiable and
render without client-side rescaling.
"""

from copy import deepcopy

VALID_EVENT_TYPES = frozenset(
    {
        "reveal",
        "win",
        "cascade",
        "removeSymbols",
        "collapse",
        "refill",
        "expandingWild",
        "freeSpinsStart",
        "freeSpin",
        "multiplierIncrease",
        "holdSpinStart",
        "holdSpinLock",
        "holdSpinRespins",
        "holdSpinEnd",
        "payout",
        "roundEnd",
    }
)


def emit(gamestate, event_type, **payload) -> dict:
    """Append a contract event to the in-flight book and return it."""
    assert event_type in VALID_EVENT_TYPES, (
        f"event '{event_type}' is outside the frontend contract: "
        f"{sorted(VALID_EVENT_TYPES)}"
    )
    event = {"index": len(gamestate.book.events), "type": event_type, **deepcopy(payload)}
    gamestate.book.add_event(event)
    return event


def json_sym(symbol) -> dict:
    """Serialize one SDK Symbol cell to the frontend SymbolData shape."""
    cell = {"name": symbol.name}
    if symbol.name == "P":
        cell["value"] = int(round(float(getattr(symbol, "prize", 0) or 0) * 100, 0))
        if getattr(symbol, "locked", False):
            cell["locked"] = True
    return cell


def board_json(board) -> list:
    """Serialize a reel-major board of SDK Symbols to the frontend Board shape."""
    return [[json_sym(cell) for cell in reel] for reel in board]


# --- reveal / cascade sequence ------------------------------------------------
def reveal(gamestate) -> dict:
    return emit(gamestate, "reveal", board=board_json(gamestate.board))


def win(gamestate, positions, amount, symbol) -> dict:
    return emit(gamestate, "win", positions=positions, amount=amount, symbol=symbol)


def cascade(gamestate, number) -> dict:
    return emit(gamestate, "cascade", cascade=number)


def remove_symbols(gamestate, positions) -> dict:
    return emit(gamestate, "removeSymbols", positions=positions)


def collapse(gamestate, board) -> dict:
    return emit(gamestate, "collapse", board=board)


def refill(gamestate, board, positions) -> dict:
    return emit(gamestate, "refill", board=board, positions=positions)


def expanding_wild(gamestate, reel, rows) -> dict:
    return emit(gamestate, "expandingWild", reel=reel, rows=rows)


# --- free spins --------------------------------------------------------------
def free_spins_start(gamestate, total, multiplier) -> dict:
    return emit(gamestate, "freeSpinsStart", total=total, multiplier=multiplier)


def free_spin(gamestate, current, total) -> dict:
    return emit(
        gamestate,
        "freeSpin",
        current=current,
        total=total,
        remaining=max(0, total - current),
    )


def multiplier_increase(gamestate, before, after, reason) -> dict:
    return emit(
        gamestate,
        "multiplierIncrease",
        **{"from": before, "to": after, "reason": reason},
    )


# --- hold & spin -------------------------------------------------------------
def hold_spin_start(gamestate, respins, locked) -> dict:
    return emit(gamestate, "holdSpinStart", respins=respins, locked=locked)


def hold_spin_lock(gamestate, locks, reset_respins) -> dict:
    return emit(gamestate, "holdSpinLock", locks=locks, resetRespins=reset_respins)


def hold_spin_respins(gamestate, remaining) -> dict:
    return emit(gamestate, "holdSpinRespins", remaining=remaining)


def hold_spin_end(gamestate, total) -> dict:
    return emit(gamestate, "holdSpinEnd", total=total)


# --- round end ---------------------------------------------------------------
def payout(gamestate, amount, total) -> dict:
    return emit(gamestate, "payout", amount=amount, total=total)


def round_end(gamestate, payout_multiplier) -> dict:
    return emit(gamestate, "roundEnd", payoutMultiplier=payout_multiplier)