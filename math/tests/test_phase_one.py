import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from black_market.game_config import GameConfig
from black_market.game_executables import GameExecutables
from black_market.gamestate import GameState
from black_market.output import write_index, write_uncompressed_mode


class PhaseOneMathTests(unittest.TestCase):
    def setUp(self):
        self.config = GameConfig()
        self.state = GameState(self.config)
        self.game = GameExecutables(self.state)
        self.board = [[{"name": "cash"} for _ in range(4)] for _ in range(5)]

    def test_event_contract_cascade_wild_multiplier_and_locks(self):
        self.game.reveal(self.board)
        positions = [{"reel": 0, "row": 0}, {"reel": 1, "row": 0}, {"reel": 2, "row": 0}]
        self.game.cascade(positions, [[{"name": "gold"}] for _ in range(5)], 2, "cash", 1)
        self.game.expanding_wild(3)
        self.game.start_free_spins(8)
        self.game.free_spin(1, 8)
        self.game.advance_multiplier("cascade")
        self.game.start_hold_spin([{"reel": 0, "row": 0, "value": 1}])
        self.game.lock_hold_symbols([{"reel": 4, "row": 3, "value": 5, "multiplier": 2}])
        self.game.use_respin()
        self.game.end_hold_spin(10)
        self.game.end_round()
        types = [event["type"] for event in self.state.events]
        self.assertEqual(types[1:6], ["win", "cascade", "removeSymbols", "collapse", "refill"])
        self.assertEqual(self.state.multiplier, 2)
        self.assertEqual(len(self.state.locked), 2)
        self.assertEqual([event["index"] for event in self.state.events], list(range(len(self.state.events))))

    def test_output_hooks_write_matching_books_lookup_and_index(self):
        self.game.reveal(self.board)
        self.game.end_round()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            mode = write_uncompressed_mode(output, self.config.bet_modes[0], [self.state.book(7)], {7: 3})
            write_index(output, [mode])
            self.assertEqual((output / "lookUpTable_base_0.csv").read_text().strip(), "7,3,0.0")
            self.assertEqual(json.loads((output / "index.json").read_text())["modes"][0]["name"], "base")


if __name__ == "__main__": unittest.main()
