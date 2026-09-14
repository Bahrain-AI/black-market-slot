"""SDK-native BLACK MARKET tests against the pinned Stake Engine Math SDK.

These tests exercise the *official* SDK pipeline directly: the overlay is staged
into the pinned checkout (``math/.stake-engine/math-sdk``) and ``GameState`` is
driven through the same run flow the Engine uses to generate result books.
Every round is validated against the typed frontend event contract
(16 event types, integer hundredths, monotonic indices, deterministic replay).

Skipped when the pinned checkout has not been bootstrapped yet
(``python math/tools/bootstrap_sdk.py``).
"""

import json
import sys
import unittest
from pathlib import Path

MATH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MATH_ROOT))

from black_market.sdk import FRONTEND_CONTRACT, stage_sdk_game

GAME_ID = "black_market"
VALID_TYPES = frozenset(FRONTEND_CONTRACT)
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


class SDKNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sdk_root = MATH_ROOT / ".stake-engine" / "math-sdk"
        if not sdk_root.is_dir():
            raise unittest.SkipTest("run python math/tools/bootstrap_sdk.py first")
        staged = stage_sdk_game(sdk_root)
        game_dir = Path(staged["target"])
        # Sibling imports in the overlay resolve against the game directory; the
        # SDK packages resolve against the checkout root.
        sys.path.insert(0, str(game_dir))
        sys.path.insert(0, str(sdk_root.resolve()))
        from game_config import GameConfig
        from gamestate import GameState
        import game_events

        cls.GameConfig = GameConfig
        cls.GameState = GameState
        cls.events = game_events
        cls.config = GameConfig()
        cls.game_dir = game_dir

    def _fresh_state(self):
        return self.GameState(self.config)

    def _run_round(self, state, sim, seed):
        state.run_spin(sim, seed)
        return state.book

    def _validate_round(self, book, mode, criteria, errors):
        events = book.events
        if not events:
            errors.append("empty book")
            return
        types = [event["type"] for event in events]
        for event_type in types:
            if event_type not in VALID_TYPES:
                errors.append(f"event type outside contract: {event_type}")
        counts = {}
        for index, event in enumerate(events):
            event_type = event["type"]
            counts[event_type] = counts.get(event_type, 0) + 1
            if event.get("index") != index:
                errors.append(f"index {event.get('index')} != position {index}")
            missing = [key for key in FRONTEND_CONTRACT[event_type] if key not in event]
            if missing:
                errors.append(f"{event_type} missing payload keys {missing}")
            if event_type == "win" and not isinstance(event["amount"], int):
                errors.append("win.amount not int hundredths")
            if event_type == "freeSpin":
                if not (
                    isinstance(event["current"], int)
                    and isinstance(event["total"], int)
                    and isinstance(event["remaining"], int)
                ):
                    errors.append("freeSpin fields not int")
            if event_type == "multiplierIncrease":
                if event["from"] not in PROGRESSION or event["to"] not in PROGRESSION:
                    errors.append("multiplierIncrease outside progression")
                if event["from"] >= event["to"]:
                    errors.append("multiplierIncrease not increasing")
            if event_type == "holdSpinLock":
                for lock in event["locks"]:
                    if not isinstance(lock.get("value"), int):
                        errors.append("holdSpinLock value not int")
            if event_type == "holdSpinStart":
                for lock in event["locked"]:
                    if not isinstance(lock.get("value"), int):
                        errors.append("holdSpinStart locked value not int")
            if event_type in ("reveal", "collapse", "refill"):
                board = event["board"]
                if len(board) != self.config.num_reels or any(
                    len(reel) != self.config.num_rows[0] for reel in board
                ):
                    errors.append(f"{event_type} board shape mismatch")
        if "cascade" in counts:
            cascade = [event["cascade"] for event in events if event["type"] == "cascade"]
            if cascade != list(range(1, len(cascade) + 1)):
                errors.append(f"cascade numbering broken: {cascade}")

        round_ends = [event for event in events if event["type"] == "roundEnd"]
        payouts = [event for event in events if event["type"] == "payout"]
        if len(round_ends) != 1 or len(payouts) != 1:
            errors.append("round must contain exactly one payout and one roundEnd")
            return
        pm = round_ends[0]["payoutMultiplier"]
        if not isinstance(pm, int) or pm != payouts[0]["amount"] or pm != payouts[0]["total"]:
            errors.append("roundEnd/payout incoherent")
        if pm != book.payout_multiplier * 100:
            errors.append("roundEnd != book payoutMultiplier")
        if abs((book.basegame_wins + book.freegame_wins) - (pm / 100.0)) > 1e-6:
            if book.basegame_wins + book.freegame_wins + 1e-9 < pm / 100.0:
                errors.append("base+free < payoutMultiplier")

        final = pm / 100.0
        fs_count = counts.get("freeSpinsStart", 0)
        hs_count = counts.get("holdSpinStart", 0)
        if criteria == "0" and final != 0:
            errors.append(f"'0' criteria won {final}")
        if criteria == "basegame" and (final <= 0 or fs_count):
            errors.append("basegame criteria unexpected fs/nonwin")
        if criteria in ("freegame", "wincap") and mode == "base" and not fs_count:
            errors.append(f"{criteria} criteria missing freespins")
        if criteria == "wincap" and final != MAX_WIN:
            errors.append(f"wincap criteria final {final} != {MAX_WIN}")
        if mode == "backroom" and (not fs_count or hs_count):
            errors.append("backroom must play free spins only")
        if mode == "vault" and (not hs_count or fs_count):
            errors.append("vault must play hold & spin only")
        if mode == "black_card" and not (fs_count and hs_count):
            errors.append("black_card must play free spins + hold & spin")

    def test_all_modes_round_contract(self):
        state = self._fresh_state()
        errors = []
        for mode, criteria in MODES:
            state.betmode = mode
            state.criteria = criteria
            for sim in range(6):
                self._validate_round(self._run_round(state, sim, 9000 + sim), mode, criteria, errors)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_free_spin_sequencing_and_multiplier_progression(self):
        state = self._fresh_state()
        state.betmode = "black_card"
        state.criteria = "hybrid"
        rounds = [self._run_round(state, sim * 31 + 1, 5000 + sim * 31) for sim in range(8)]
        errors = []
        for book in rounds:
            fs_events = [event for event in book.events if event["type"] == "freeSpin"]
            if not fs_events:
                errors.append("hybrid round missing free spins")
                continue
            currents = [event["current"] for event in fs_events]
            if currents != list(range(1, len(currents) + 1)):
                errors.append(f"freeSpin current sequence broken: {currents[:8]}")
            for event in fs_events:
                if event["remaining"] != max(0, event["total"] - event["current"]):
                    errors.append("freeSpin remaining mismatch")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_hold_spin_sequencing_and_locked_total(self):
        state = self._fresh_state()
        state.betmode = "vault"
        state.criteria = "holdspin"
        errors = []
        for sim in range(8):
            book = self._run_round(state, sim, 7000 + sim)
            starts = [event for event in book.events if event["type"] == "holdSpinStart"]
            ends = [event for event in book.events if event["type"] == "holdSpinEnd"]
            if len(starts) != 1 or len(ends) != 1:
                errors.append("vault round missing holdSpinStart/holdSpinEnd")
                continue
            locked_total = sum(lock["value"] for lock in starts[0]["locked"])
            for event in book.events:
                if event["type"] == "holdSpinLock":
                    locked_total += sum(lock["value"] for lock in event["locks"])
            if ends[0]["total"] != locked_total:
                errors.append(f"holdSpinEnd {ends[0]['total']} != locked {locked_total}")
            respins = [
                event["remaining"]
                for event in book.events
                if event["type"] == "holdSpinRespins"
            ]
            for index in range(1, len(respins)):
                if not (
                    respins[index] == respins[index - 1] - 1
                    or respins[index] == self.config.holdspin_respins - 1
                ):
                    errors.append(f"holdSpinRespins sequence broken: {respins[:10]}")
                    break
        self.assertEqual(errors, [], "\n".join(errors))

    def test_deterministic_replay_across_modes(self):
        first = self._fresh_state()
        second = self._fresh_state()
        mismatches = []
        for mode, criteria in MODES:
            for seed in (111, 222, 333):
                first.betmode = mode
                first.criteria = criteria
                first.run_spin(seed, seed)
                a = json.dumps(first.book.events, sort_keys=True) + "|" + str(first.book.payout_multiplier)
                second.betmode = mode
                second.criteria = criteria
                second.run_spin(seed, seed)
                b = json.dumps(second.book.events, sort_keys=True) + "|" + str(second.book.payout_multiplier)
                if a != b:
                    mismatches.append(f"{mode}/{criteria} seed {seed}")
        self.assertEqual(mismatches, [], "\n".join(mismatches))

    def test_wallet_accumulation_matches_book(self):
        # The Engine wallet (win_manager) is the authority: the RGS wallet balance
        # change for a round must equal exactly what the published book carries.
        # Book.payout_multiplier is an in-memory float multiplier; the JSON field
        # is int hundredths (Book.to_json: int(round(pm * 100))).
        state = self._fresh_state()
        state.betmode = "base"
        state.criteria = "freegame"
        for sim in range(4):
            seed = 12340 + sim
            state.run_spin(sim, seed)
            capped = round(min(state.win_manager.running_bet_win, state.config.wincap), 2)
            # In-memory book agreed with the wallet.
            self.assertAlmostEqual(state.book.payout_multiplier, capped, places=2)
            # Published book (int hundredths) round-trips the same amount.
            json_book = state.book.to_json()
            self.assertEqual(json_book["payoutMultiplier"], int(round(capped * 100, 0)))
            # Wincap honoured: no published book may exceed max win in hundredths.
            self.assertLessEqual(json_book["payoutMultiplier"], int(state.config.wincap * 100))


if __name__ == "__main__":
    unittest.main()