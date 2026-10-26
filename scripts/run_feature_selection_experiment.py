#!/usr/bin/env python3
"""Run the TCM-SD feature-selection ablation (train-only selectors)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tcm_ml.feature_selection_experiment import run_feature_selection_experiment


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=2000, help="Features kept after ranking")
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    summary = run_feature_selection_experiment(
        root=ROOT,
        k=args.k,
        random_state=args.random_state,
    )
    print("\nDone.")
    print(f"Comparison CSV: {summary['results_csv']}")
    print(f"F1 deltas CSV: {summary['deltas_csv']}")
    print(f"Write-up: {summary['interpretation']}")


if __name__ == "__main__":
    main()
