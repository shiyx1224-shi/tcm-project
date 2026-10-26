#!/usr/bin/env python3
"""Re-run overlap / leakage assertions on saved partitions."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tcm_ml.checks import assert_no_feature_label_leakage, assert_no_split_overlap
from tcm_ml.load import TEXT_FEATURE_COLS


def main() -> None:
    processed = ROOT / "data" / "processed"
    parts = {
        name: pd.read_parquet(processed / f"{name}_rows.parquet")
        for name in ("train", "validation", "test")
    }
    overlap = assert_no_split_overlap(parts)
    leakage = assert_no_feature_label_leakage(TEXT_FEATURE_COLS)
    print(json.dumps({"overlap": overlap, "leakage": leakage}, indent=2))
    print("All split overlap and feature-leakage checks passed.")


if __name__ == "__main__":
    main()
