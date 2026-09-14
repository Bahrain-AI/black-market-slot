from copy import deepcopy

Board = list[list[dict]]
Position = dict[str, int]


def expand_wild(board: Board, reel: int) -> tuple[Board, list[int]]:
    result = deepcopy(board)
    rows = list(range(len(result[reel])))
    for row in rows:
        result[reel][row] = {"name": "wild"}
    return result, rows


def remove_and_collapse(board: Board, positions: list[Position], refill_symbols: list[list[dict]]) -> tuple[Board, Board, list[Position]]:
    """Return the post-removal collapse snapshot and final refill snapshot.

    Boards are reel-major. Refill symbols are supplied by the simulator/RNG layer,
    keeping event calculation deterministic and directly testable.
    """
    removed = {(item["reel"], item["row"]) for item in positions}
    collapsed: Board = []
    final: Board = []
    refill_positions: list[Position] = []
    for reel_index, reel in enumerate(board):
        survivors = [deepcopy(symbol) for row, symbol in enumerate(reel) if (reel_index, row) not in removed]
        missing = len(reel) - len(survivors)
        empty = [{"name": "empty"} for _ in range(missing)]
        collapsed.append(empty + survivors)
        additions = [deepcopy(symbol) for symbol in refill_symbols[reel_index][:missing]]
        final.append(additions + survivors)
        refill_positions.extend({"reel": reel_index, "row": row} for row in range(missing))
    return collapsed, final, refill_positions


def next_multiplier(current: int, progression: tuple[int, ...]) -> int:
    try: return progression[min(progression.index(current) + 1, len(progression) - 1)]
    except ValueError as exc: raise ValueError(f"{current} is not in multiplier progression") from exc
