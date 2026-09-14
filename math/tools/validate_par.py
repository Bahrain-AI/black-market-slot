"""Validate final BLACK MARKET PAR metrics against an approved manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_approved_inputs import METRICS, MODES, ApprovalValidationError, validate_approval_manifest


class ParValidationError(ValueError):
    """Raised when final statistics do not meet the signed PAR approval."""


def _number(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise ParValidationError(f"{label} must be a non-negative number")
    return float(value)


def validate_par_metrics(statistics: Any, approval: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(statistics, dict):
        raise ParValidationError("statistics must be an object")
    metrics = statistics.get("parMetrics")
    if not isinstance(metrics, dict) or set(metrics) != set(MODES):
        raise ParValidationError(f"statistics.parMetrics must contain exactly: {', '.join(MODES)}")

    report: dict[str, Any] = {"modes": {}}
    rtps: list[float] = []
    for mode in MODES:
        values = metrics[mode]
        if not isinstance(values, dict):
            raise ParValidationError(f"statistics.parMetrics.{mode} must be an object")
        rtp = _number(values.get("rtp"), f"statistics.parMetrics.{mode}.rtp")
        if not 0.90 <= rtp <= 0.98:
            raise ParValidationError(f"RTP for {mode} must be between 0.90 and 0.98; got {rtp}")
        rtps.append(rtp)
        mode_report = {"rtp": rtp}
        bounds_by_metric = approval["par"]["metrics"][mode]
        for metric in METRICS:
            value = _number(values.get(metric), f"statistics.parMetrics.{mode}.{metric}")
            bounds = bounds_by_metric[metric]
            if not bounds["min"] <= value <= bounds["max"]:
                raise ParValidationError(
                    f"{metric} for {mode} is {value}; approved range is {bounds['min']}..{bounds['max']}"
                )
            mode_report[metric] = value
        report["modes"][mode] = mode_report
    spread = max(rtps) - min(rtps)
    if spread > 0.005:
        raise ParValidationError(f"RTP spread is {spread:.6f}; maximum is 0.005")
    report["rtpSpread"] = spread
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--statistics", required=True, type=Path)
    parser.add_argument("--approval", required=True, type=Path)
    args = parser.parse_args()
    try:
        approval_data = json.loads(args.approval.read_text(encoding="utf-8"))
        approval = validate_approval_manifest(approval_data, args.approval.parent)
        statistics = json.loads(args.statistics.read_text(encoding="utf-8"))
        report = validate_par_metrics(statistics, approval)
    except (OSError, json.JSONDecodeError, ApprovalValidationError, ParValidationError) as exc:
        print(f"error: {exc}")
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
