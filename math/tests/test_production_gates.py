import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

MATH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MATH_ROOT / "tools"))
sys.path.insert(0, str(MATH_ROOT.parent / "tools" / "submission"))

from validate_approved_inputs import ApprovalValidationError, validate_input_directory
from validate_par import ParValidationError, validate_par_metrics
from validate_delivery import ReleaseEligibilityError, assert_release_eligible
from validate_assets import AssetValidationError, validate_manifest
from build_tile_package import TileSourceError, validate_release_sources


MODES = ("base", "backroom", "vault", "black_card")


def _bounds(minimum: float, maximum: float) -> dict[str, float]:
    return {"min": minimum, "max": maximum}


def _approval(source_hash: str, *, provisional: bool = False) -> dict:
    modes = {
        mode: {
            "rtp": 0.96,
            "cost": {"base": 1, "backroom": 60, "vault": 100, "black_card": 200}[mode],
        }
        for mode in MODES
    }
    metrics = {
        mode: {
            "maxWinFrequency": _bounds(0.0005, 0.0015),
            "hitRate": _bounds(0.20, 0.30),
            "volatility": _bounds(1.0, 2.0),
            "featureFrequency": _bounds(0.01, 0.10),
        }
        for mode in MODES
    }
    return {
        "schemaVersion": 1,
        "provisional": provisional,
        "approval": {
            "version": "2026.09.14",
            "approver": "Approved Math Team",
            "date": "2026-09-14",
            "signedSource": {"path": "signed-source.json", "sha256": source_hash},
        },
        "sourceFiles": [{"path": "signed-source.json", "sha256": source_hash}],
        "modes": modes,
        "maximumWin": 5000,
        "par": {"metrics": metrics},
    }


class ProductionGateTests(unittest.TestCase):
    def _approved_directory(self, *, provisional: bool = False) -> Path:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        (root / "schema.json").write_text(
            (MATH_ROOT / "approved-inputs" / "schema.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        source = root / "signed-source.json"
        source.write_text('{"signed":true}\n', encoding="utf-8")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        (root / "approval.json").write_text(
            json.dumps(_approval(digest, provisional=provisional)), encoding="utf-8"
        )
        return root

    def tearDown(self):
        if hasattr(self, "tempdir"):
            self.tempdir.cleanup()

    def test_valid_approved_inputs_require_hashed_signed_source_and_all_modes(self):
        approval = validate_input_directory(self._approved_directory())
        self.assertFalse(approval["provisional"])
        self.assertEqual(set(approval["modes"]), set(MODES))

    def test_provisional_approval_manifest_is_rejected(self):
        with self.assertRaisesRegex(ApprovalValidationError, "provisional"):
            validate_input_directory(self._approved_directory(provisional=True))

    def test_par_metrics_enforce_rtp_spread_and_approved_bounds(self):
        approval = validate_input_directory(self._approved_directory())
        statistics = {
            "parMetrics": {
                mode: {
                    "rtp": 0.96,
                    "maxWinFrequency": 0.001,
                    "hitRate": 0.25,
                    "volatility": 1.5,
                    "featureFrequency": 0.05,
                }
                for mode in MODES
            }
        }
        report = validate_par_metrics(statistics, approval)
        self.assertEqual(report["rtpSpread"], 0.0)

        statistics["parMetrics"]["base"]["rtp"] = 0.99
        with self.assertRaisesRegex(ParValidationError, "RTP"):
            validate_par_metrics(statistics, approval)

    def test_release_validation_rejects_provisional_artifacts(self):
        with tempfile.TemporaryDirectory() as folder:
            package = Path(folder)
            (package / "provisional-summary.json").write_text(
                json.dumps({"provisional": True}), encoding="utf-8"
            )
            with self.assertRaisesRegex(ReleaseEligibilityError, "provisional"):
                assert_release_eligible(package)

    def test_empty_non_release_asset_manifest_is_valid_for_current_state(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "licenses.json"
            manifest.write_text(
                json.dumps({"schemaVersion": 1, "release": False, "assets": [], "audio": "none"}),
                encoding="utf-8",
            )
            report = validate_manifest(manifest)
            self.assertEqual(report["assetCount"], 0)

    def test_asset_manifest_rejects_hash_mismatches(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            image = root / "symbol.webp"
            image.write_bytes(b"production-art")
            manifest = root / "licenses.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "release": False,
                        "audio": "none",
                        "assets": [
                            {
                                "path": "symbol.webp",
                                "sha256": "0" * 64,
                                "creatorLicensor": "Artist",
                                "licenceGrant": "Project licence",
                                "approvalDate": "2026-09-14",
                                "sourceFile": "source.psd",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(AssetValidationError, "sha256"):
                validate_manifest(manifest)

    def test_release_tile_builder_refuses_reference_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            background = root / "reference-background.png"
            foreground = root / "foreground.png"
            logo = root / "logo.png"
            for path in (background, foreground, logo):
                path.write_bytes(b"image")
            with self.assertRaisesRegex(TileSourceError, "reference"):
                validate_release_sources(background, foreground, logo)


if __name__ == "__main__":
    unittest.main()
