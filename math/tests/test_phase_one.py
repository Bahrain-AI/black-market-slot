import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from black_market.game_config import GameConfig
from black_market.game_executables import GameExecutables
from black_market.gamestate import GameState
from black_market.output import (
    compress_jsonl,
    validate_artifacts,
    write_index,
    write_uncompressed_mode,
)
from black_market.sdk import (
    SDK_COMMIT,
    SDK_REPOSITORY,
    SDK_REQUIRED_SYMBOLS,
    OVERLAY_REQUIRED_FILES,
    stage_sdk_game,
    validate_sdk_checkout,
)


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
            self.assertEqual((output / "lookUpTable_base_0.csv").read_text().strip(), "7,3,0")
            self.assertEqual(json.loads((output / "index.json").read_text())["modes"][0]["name"], "base")

    def test_compressed_artifacts_are_cross_checked_and_report_weighted_rtp(self):
        self.game.reveal(self.board)
        self.game.end_round()
        losing_book = self.state.book(0)
        winning_book = {**losing_book, "id": 1, "payoutMultiplier": 200}
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            mode = write_uncompressed_mode(
                output,
                self.config.bet_modes[0],
                [losing_book, winning_book],
                {0: 1, 1: 1},
            )
            source = output / mode["events"]
            compressed = source.with_suffix(source.suffix + ".zst")
            compress_jsonl(source, compressed)
            source.unlink()
            mode["events"] = compressed.name
            write_index(output, [mode])

            report = validate_artifacts(output)

            self.assertEqual(report["modes"][0]["bookCount"], 2)
            self.assertEqual(report["modes"][0]["weightedRtp"], 1.0)
            self.assertTrue(report["modes"][0]["compressed"])

    def test_artifact_validation_rejects_lookup_payout_mismatch(self):
        self.game.reveal(self.board)
        self.game.end_round()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            mode = write_uncompressed_mode(output, self.config.bet_modes[0], [self.state.book(7)], {7: 3})
            (output / mode["weights"]).write_text("7,3,10\n", encoding="utf-8")
            write_index(output, [mode])
            with self.assertRaisesRegex(ValueError, "payout mismatch"):
                validate_artifacts(output)

    def test_sdk_checkout_requires_the_pinned_official_revision(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "src/config").mkdir(parents=True)
            (root / "src/events").mkdir(parents=True)
            (root / "src/state").mkdir(parents=True)
            (root / "src/write_data").mkdir(parents=True)
            (root / "utils").mkdir()
            for relative, symbols in SDK_REQUIRED_SYMBOLS.items():
                definitions = "\n".join(f"def {name}(): pass" for name in symbols)
                (root / relative).write_text(definitions + "\n", encoding="utf-8")
            (root / ".stake-engine-revision").write_text(SDK_COMMIT, encoding="utf-8")

            report = validate_sdk_checkout(root, allow_revision_marker=True)

            self.assertEqual(report["repository"], SDK_REPOSITORY)
            self.assertEqual(report["commit"], SDK_COMMIT)

            source = root / "overlay"
            (source / "reels").mkdir(parents=True)
            for name in OVERLAY_REQUIRED_FILES:
                (source / name).write_text("PROVISIONAL = True\n", encoding="utf-8")
            (source / "reels/BR0.csv").write_text("H1,H1,H1,H1,H1\n", encoding="utf-8")
            staged = stage_sdk_game(root, source=source, allow_revision_marker=True)
            self.assertEqual(staged["gameId"], "black_market")
            self.assertTrue((root / "games/black_market/game_config.py").is_file())


if __name__ == "__main__": unittest.main()
