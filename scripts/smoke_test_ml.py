#!/usr/bin/env python3
"""End-to-end smoke checks for the TCM-SD ML pipeline (no full retrain)."""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _ok(msg: str) -> None:
    print(f"[OK] {msg}")


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}", file=sys.stderr)
    raise SystemExit(1)


def check_dataset_link() -> None:
    url = "https://github.com/Borororo/ZY-BERT"
    with urllib.request.urlopen(url, timeout=30) as resp:
        if resp.status != 200:
            _fail(f"Dataset page HTTP {resp.status}: {url}")
    raw = "https://raw.githubusercontent.com/Borororo/ZY-BERT/main/test.json"
    with urllib.request.urlopen(raw, timeout=60) as resp:
        chunk = resp.read(64)
        if not chunk:
            _fail(f"Empty download from {raw}")
    _ok("Public dataset link and raw test.json are reachable")


def check_local_data() -> None:
    raw = ROOT / "data" / "raw" / "TCM-SD"
    for name in ("test.json", "TCM_SD_train_dev.zip"):
        if not (raw / name).exists():
            _fail(f"Missing {raw / name}; run bash scripts/download_tcm_sd.sh")
    # train.json may need unzip
    from tcm_ml.load import load_tcm_sd

    df = load_tcm_sd(ROOT)
    if len(df) < 50000:
        _fail(f"Unexpected row count after load: {len(df)}")
    _ok(f"Loaded TCM-SD locally ({len(df)} rows)")


def check_splits_and_leakage() -> None:
    import pandas as pd
    from tcm_ml.checks import assert_no_feature_label_leakage, assert_no_split_overlap
    from tcm_ml.load import TEXT_FEATURE_COLS

    processed = ROOT / "data" / "processed"
    parts = {
        name: pd.read_parquet(processed / f"{name}_rows.parquet")
        for name in ("train", "validation", "test")
    }
    overlap = assert_no_split_overlap(parts)
    leakage = assert_no_feature_label_leakage(TEXT_FEATURE_COLS)
    if not overlap["ok"] or not leakage["ok"]:
        _fail(f"Leakage/overlap failed: {overlap} {leakage}")
    _ok("Split overlap and feature-leakage checks passed")


def check_results_present() -> None:
    need = [
        ROOT / "results" / "metrics" / "model_comparison.csv",
        ROOT / "results" / "figures" / "model_comparison.png",
        ROOT / "results" / "metrics" / "final_test_summary.json",
        ROOT / "results" / "figures" / "final_f1_comparison.png",
        ROOT / "docs" / "final_evaluation.md",
    ]
    for path in need:
        if not path.exists():
            _fail(f"Missing expected artifact: {path}")
    summary = json.loads((ROOT / "results" / "metrics" / "final_test_summary.json").read_text())
    if summary.get("selection", {}).get("model") != "svm":
        _fail(f"Unexpected selected model in final summary: {summary.get('selection')}")
    _ok("Core results / graphs / final evaluation artifacts present")


def check_svm_predict() -> None:
    from tcm_ml.svm import SyndromeSVMPipeline

    model_dir = ROOT / "artifacts" / "models" / "svm"
    if not (model_dir / "syndrome_svm_pipeline.joblib").exists():
        # Fall back: model-only + preprocessor must exist for training path
        if not (model_dir / "svm_model.joblib").exists():
            _fail("Missing SVM artifacts; run python scripts/train_svm.py")
        _ok("SVM model joblib present (pipeline missing but model available)")
        return
    pipe = SyndromeSVMPipeline.load(model_dir)
    out = pipe.predict_records(
        [
            {
                "chief_complaint": "头痛，头晕",
                "description": "患者头痛头晕三日，伴恶心。",
                "detection": "舌淡红，苔薄白，脉弦。",
            }
        ]
    )
    if not out or "predicted_norm_syndrome" not in out[0]:
        _fail(f"Unexpected SVM predict output: {out}")
    _ok(f"SVM predict works → {out[0]['predicted_norm_syndrome']}")


def check_compare_and_final() -> None:
    from tcm_ml.compare_models import write_model_comparison
    from tcm_ml.final_evaluation import select_best_model, verify_integrity

    paths = write_model_comparison(ROOT)
    for key in ("csv", "figure"):
        if not Path(paths[key]).exists():
            _fail(f"compare_models missing {key}: {paths[key]}")
    decision = select_best_model(ROOT)
    integrity = verify_integrity(ROOT)
    if decision["selected_model"] != "svm":
        _fail(f"Selection mismatch: {decision['selected_model']}")
    if not integrity["ok"]:
        _fail(f"Integrity failed: {integrity}")
    _ok("compare_models + selection/integrity helpers reproduce")


def main() -> None:
    check_dataset_link()
    check_local_data()
    check_splits_and_leakage()
    check_results_present()
    check_svm_predict()
    check_compare_and_final()
    print("\nAll smoke tests passed.")


if __name__ == "__main__":
    main()
