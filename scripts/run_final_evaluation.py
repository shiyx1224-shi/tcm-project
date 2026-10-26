#!/usr/bin/env python3
"""Lock the best validation model, verify integrity, then score untouched test."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tcm_ml.final_evaluation import run_final_evaluation


def main() -> None:
    result = run_final_evaluation(ROOT)
    print(json.dumps(
        {
            "selected_model": result["decision"]["selected_model"],
            "validation_micro_f1": result["decision"]["validation_micro_f1"],
            "test_micro_f1": result["test_summary"]["micro_f1"],
            "test_macro_f1": result["test_summary"]["macro_f1"],
            "integrity_ok": result["integrity"]["ok"],
            "report": result["report"],
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
