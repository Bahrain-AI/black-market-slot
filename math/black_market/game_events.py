from copy import deepcopy
from typing import Any


def event(event_type: str, **fields: Any) -> dict[str, Any]:
    return {"type": event_type, **deepcopy(fields)}


def reveal(board: list[list[dict]]) -> dict: return event("reveal", board=board)
def win(positions: list[dict], amount: float, symbol: str) -> dict: return event("win", positions=positions, amount=amount, symbol=symbol)
def cascade(number: int) -> dict: return event("cascade", cascade=number)
def remove_symbols(positions: list[dict]) -> dict: return event("removeSymbols", positions=positions)
def collapse(board: list[list[dict]]) -> dict: return event("collapse", board=board)
def refill(board: list[list[dict]], positions: list[dict]) -> dict: return event("refill", board=board, positions=positions)
def expanding_wild(reel: int, rows: list[int]) -> dict: return event("expandingWild", reel=reel, rows=rows)
def free_spins_start(total: int, multiplier: int) -> dict: return event("freeSpinsStart", total=total, multiplier=multiplier)
def free_spin(current: int, total: int, remaining: int) -> dict: return event("freeSpin", current=current, total=total, remaining=remaining)
def multiplier_increase(before: int, after: int, reason: str) -> dict: return event("multiplierIncrease", **{"from": before, "to": after, "reason": reason})
def hold_spin_start(respins: int, locked: list[dict]) -> dict: return event("holdSpinStart", respins=respins, locked=locked)
def hold_spin_lock(locks: list[dict], reset_respins: int | None = None) -> dict:
    fields: dict[str, Any] = {"locks": locks}
    if reset_respins is not None: fields["resetRespins"] = reset_respins
    return event("holdSpinLock", **fields)
def hold_spin_respins(remaining: int) -> dict: return event("holdSpinRespins", remaining=remaining)
def hold_spin_end(total: float) -> dict: return event("holdSpinEnd", total=total)
def payout(amount: float, total: float) -> dict: return event("payout", amount=amount, total=total)
def round_end(payout_multiplier: float) -> dict: return event("roundEnd", payoutMultiplier=payout_multiplier)
