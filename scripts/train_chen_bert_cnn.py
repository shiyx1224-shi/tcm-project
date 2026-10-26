#!/usr/bin/env python3
"""Train Chen et al. 2024–inspired BERT+TextCNN adaptation on TCM-SD.

Same train/validation partitions as existing models. Not an exact reproduction.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tcm_ml.chen_bert_cnn.train import train_chen_bert_cnn


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", type=str, default="hfl/rbt3")
    parser.add_argument("--max-length", type=int, default=96)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=24)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    result = train_chen_bert_cnn(
        root=ROOT,
        model_name=args.model_name,
        max_length=args.max_length,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        dropout=args.dropout,
        seed=args.seed,
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
    print("Test unused. Exact Chen TCM-BERT-CNN reproduction is NOT claimed.")


if __name__ == "__main__":
    main()
