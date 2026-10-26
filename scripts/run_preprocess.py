#!/usr/bin/env python3
"""Build leakage-aware splits and train-fitted preprocessing artifacts.

Does not train a classifier.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tcm_ml.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--max-tfidf-features", type=int, default=20000)
    parser.add_argument("--select-k", type=int, default=5000)
    args = parser.parse_args()

    report = run_pipeline(
        root=ROOT,
        random_state=args.random_state,
        max_tfidf_features=args.max_tfidf_features,
        select_k=args.select_k,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nWrote data/processed/ and artifacts/preprocess/")
    print("No classifier was trained.")


if __name__ == "__main__":
    main()
