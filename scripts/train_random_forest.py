#!/usr/bin/env python3
"""Train the initial multiclass Random Forest on prepared TCM-SD features.

Uses train for fitting and validation for metrics. Does not touch the test set.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tcm_ml.random_forest import train_random_forest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=40)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--n-jobs", type=int, default=4)
    args = parser.parse_args()

    result = train_random_forest(
        root=ROOT,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        random_state=args.random_state,
        n_jobs=args.n_jobs,
    )
    summary = result["validation_summary"]
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nArtifacts: {result['artifacts']}")
    print(
        "Validation — "
        f"accuracy={summary['accuracy']:.4f}  "
        f"precision={summary['precision']:.4f}  "
        f"recall={summary['recall']:.4f}  "
        f"micro_f1={summary['micro_f1']:.4f}  "
        f"macro_f1={summary['macro_f1']:.4f}"
    )
    print("Test partition was not used.")


if __name__ == "__main__":
    main()
