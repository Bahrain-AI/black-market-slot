"""Stake Math SDK integration seam.

When the official SDK is vendored or installed, subclass its GameState here and
delegate board creation/win evaluation to the SDK while retaining the event
contract in game_events.py. Phase 1 intentionally has no fallback RNG.
"""

from .gamestate import GameState


class BlackMarketGameState(GameState):
    pass
