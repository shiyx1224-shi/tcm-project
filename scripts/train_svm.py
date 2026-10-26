#!/usr/bin/env python3
"""Train multiclass Linear SVM on the same TCM-SD features as RF and LR.

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

from tcm_ml.compare_models import write_model_comparison
from tcm_ml.svm import train_svm


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--C", type=float, default=1.0)
    parser.add_argument("--max-iter", type=int, default=5000)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--skip-comparison",
        action="store_true",
        help="Do not rewrite results/metrics comparison artifacts",
    )
    args = parser.parse_args()

    result = train_svm(
        root=ROOT,
        C=args.C,
        max_iter=args.max_iter,
        random_state=args.random_state,
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

    if not args.skip_comparison:
        paths = write_model_comparison(ROOT)
        print(f"Wrote comparison CSV: {paths['csv']}")
        print(f"Wrote comparison figure: {paths['figure']}")


if __name__ == "__main__":
    main()
