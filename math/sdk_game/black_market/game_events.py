"""BLACK MARKET events mapped to the frontend contract."""

from copy import deepcopy


def emit(gamestate, event_type, **payload):
    event = {"index": len(gamestate.book.events), "type": event_type, **deepcopy(payload)}
    gamestate.book.add_event(event)
    return event


def reveal(gamestate, board): return emit(gamestate, "reveal", board=board)
def win(gamestate, positions, amount, symbol): return emit(gamestate, "win", positions=positions, amount=amount, symbol=symbol)
def cascade(gamestate, number): return emit(gamestate, "cascade", cascade=number)
def remove_symbols(gamestate, positions): return emit(gamestate, "removeSymbols", positions=positions)
def collapse(gamestate, board): return emit(gamestate, "collapse", board=board)
def refill(gamestate, board, positions): return emit(gamestate, "refill", board=board, positions=positions)
def expanding_wild(gamestate, reel, rows): return emit(gamestate, "expandingWild", reel=reel, rows=rows)
def free_spins_start(gamestate, total, multiplier): return emit(gamestate, "freeSpinsStart", total=total, multiplier=multiplier)
def free_spin(gamestate, current, total): return emit(gamestate, "freeSpin", current=current, total=total, remaining=max(0, total-current))
def multiplier_increase(gamestate, before, after, reason): return emit(gamestate, "multiplierIncrease", **{"from": before, "to": after, "reason": reason})
def hold_spin_start(gamestate, respins, locked): return emit(gamestate, "holdSpinStart", respins=respins, locked=locked)
def hold_spin_lock(gamestate, locks, reset_respins): return emit(gamestate, "holdSpinLock", locks=locks, resetRespins=reset_respins)
def hold_spin_respins(gamestate, remaining): return emit(gamestate, "holdSpinRespins", remaining=remaining)
def hold_spin_end(gamestate, total): return emit(gamestate, "holdSpinEnd", total=total)
def payout(gamestate, amount, total): return emit(gamestate, "payout", amount=amount, total=total)
def round_end(gamestate, payout_multiplier): return emit(gamestate, "roundEnd", payoutMultiplier=payout_multiplier)
