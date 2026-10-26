#!/usr/bin/env python3
"""Write results/metrics comparison CSV + figure from saved validation summaries."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tcm_ml.compare_models import build_comparison_frame, write_model_comparison


def main() -> None:
    paths = write_model_comparison(ROOT)
    frame = build_comparison_frame(ROOT)
    print(frame.to_string(index=False))
    print(f"\nWrote {paths['csv']}")
    print(f"Wrote {paths['markdown']}")
    print(f"Wrote {paths['figure']}")


if __name__ == "__main__":
    main()
