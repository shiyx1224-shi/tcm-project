#!/usr/bin/env python3
"""Load the trained SVM pipeline and predict TCM syndrome labels."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tcm_ml.load import TEXT_FEATURE_COLS
from tcm_ml.svm import SyndromeSVMPipeline

DEFAULT_ARTIFACTS = ROOT / "artifacts" / "models" / "svm"


def _records_from_args(args: argparse.Namespace) -> list[dict[str, str]]:
    if args.json:
        payload = json.loads(Path(args.json).read_text(encoding="utf-8"))
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
    parser.add_argument("--artifacts", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--chief-complaint", type=str, default="")
    parser.add_argument("--description", type=str, default="")
    parser.add_argument("--detection", type=str, default="")
    parser.add_argument("--json", type=str, default="")
    args = parser.parse_args()

    pipeline_path = args.artifacts / "syndrome_svm_pipeline.joblib"
    if not pipeline_path.exists():
        raise SystemExit(
            f"Missing {pipeline_path}. Train first with: python scripts/train_svm.py"
        )

    pipeline = SyndromeSVMPipeline.load(args.artifacts)
    print(json.dumps(pipeline.predict_records(_records_from_args(args)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
