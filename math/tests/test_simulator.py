import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from black_market.game_config import GameConfig
from black_market.output import validate_book
from black_market.simulator import Simulator, find_clusters

OVERLAY_REELS = Path(__file__).parents[1] / "sdk_game" / "black_market" / "reels"


class SimulatorTests(unittest.TestCase):
    def setUp(self):
        self.config = GameConfig()

    def test_seeded_generation_is_deterministic(self):
        def payouts(seed):
            return [book["payoutMultiplier"] for book in Simulator(self.config, "base", OVERLAY_REELS, seed).rounds(500)]

        self.assertEqual(payouts(11), payouts(11))
        self.assertNotEqual(payouts(11), payouts(12))

    def test_every_book_matches_the_engine_contract(self):
        for mode in ("base", "backroom", "vault", "black_card"):
            for book in Simulator(self.config, mode, OVERLAY_REELS, seed=3).rounds(100):
                validate_book(book)
                self.assertLessEqual(book["payoutMultiplier"], 500_000)

    def test_forced_feature_modes_contain_the_expected_events(self):
        backroom = Simulator(self.config, "backroom", OVERLAY_REELS, seed=5).rounds(100)
        vault = Simulator(self.config, "vault", OVERLAY_REELS, seed=5).rounds(100)
        hybrid = Simulator(self.config, "black_card", OVERLAY_REELS, seed=5).rounds(100)
        for book in backroom:
            self.assertIn("freeSpinsStart", [e["type"] for e in book["events"]])
        for book in vault:
            self.assertIn("holdSpinStart", [e["type"] for e in book["events"]])
        for book in hybrid:
            types = [e["type"] for e in book["events"]]
            self.assertIn("freeSpinsStart", types)
            self.assertIn("holdSpinStart", types)

    def test_cluster_detection_uses_paytable_bands(self):
        board = []
        for reel in range(5):
            board.append([{"name": "H1"} if reel in (0, 1) and row < 4 else {"name": "L3"} for row in range(4)]
                         if reel in (0, 1) else [{"name": "L3"} for _ in range(4)])
        board[3] = [{"name": "L3"} for _ in range(4)]
        board[4] = [{"name": "L3"} for _ in range(4)]
        board[4][0] = {"name": "W"}
        clusters = find_clusters(board)
        cluster = next(c for c in clusters if c["symbol"] == "H1")
        self.assertEqual(cluster["count"], 8)
        self.assertEqual(cluster["amount"], 2.0)  # band (8, 9)


if __name__ == "__main__":
    unittest.main()