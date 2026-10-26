#!/usr/bin/env python3
"""Train the Huang et al. 2022–inspired Cross-FGCNN adaptation on TCM-SD.

Uses the same train/validation partitions as RF / LR / SVM. Does not touch test.
This is an adaptation — not an exact reproduction of the dysmenorrhea Cross-FGCNN.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tcm_ml.huang_cnn.train import train_huang_cnn


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--embed-dim", type=int, default=32)
    parser.add_argument("--cross-layers", type=int, default=6)
    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    result = train_huang_cnn(
        root=ROOT,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        embed_dim=args.embed_dim,
        n_cross_layers=args.cross_layers,
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
        f"macro_f1={summary['macro_f1']:.4f}  "
        f"log_loss={summary.get('log_loss')}"
    )
    print("Test partition was not used. Exact Huang reproduction is NOT claimed.")


if __name__ == "__main__":
    main()
