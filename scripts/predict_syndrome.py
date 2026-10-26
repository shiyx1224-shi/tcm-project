#!/usr/bin/env python3
"""Load the trained Random Forest pipeline and predict TCM syndrome labels.

Examples:
  python scripts/predict_syndrome.py \\
    --chief-complaint "头痛，头晕" \\
    --description "患者头痛头晕三日，伴恶心。" \\
    --detection "舌淡红，苔薄白，脉弦。"

  python scripts/predict_syndrome.py --json path/to/records.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tcm_ml.load import TEXT_FEATURE_COLS
from tcm_ml.random_forest import SyndromeRandomForestPipeline


DEFAULT_ARTIFACTS = ROOT / "artifacts" / "models" / "random_forest"


def _records_from_args(args: argparse.Namespace) -> list[dict[str, str]]:
    if args.json:
        path = Path(args.json)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return [payload]
        if isinstance(payload, list):
            return payload
        raise ValueError("JSON input must be an object or a list of objects.")

    record = {
        "chief_complaint": args.chief_complaint or "",
        "description": args.description or "",
        "detection": args.detection or "",
    }
    if not any(str(record[c]).strip() for c in TEXT_FEATURE_COLS):
        raise SystemExit(
            "Provide at least one of --chief-complaint / --description / --detection, "
            "or pass --json with clinical text fields."
        )
    return [record]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifacts",
        type=Path,
        default=DEFAULT_ARTIFACTS,
        help="Directory with syndrome_rf_pipeline.joblib",
    )
    parser.add_argument("--chief-complaint", type=str, default="")
    parser.add_argument("--description", type=str, default="")
    parser.add_argument("--detection", type=str, default="")
    parser.add_argument(
        "--json",
        type=str,
        default="",
        help="Path to a JSON object or list of objects with clinical text fields",
    )
    args = parser.parse_args()

    pipeline_path = args.artifacts / "syndrome_rf_pipeline.joblib"
    if not pipeline_path.exists():
        raise SystemExit(
            f"Missing {pipeline_path}. Train first with: python scripts/train_random_forest.py"
        )

    pipeline = SyndromeRandomForestPipeline.load(args.artifacts)
    records = _records_from_args(args)
    predictions = pipeline.predict_records(records)
    print(json.dumps(predictions, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
