"""End-to-end split + preprocess runner (no classifier training)."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from scipy import sparse

from .checks import (
    assert_no_feature_label_leakage,
    assert_no_split_overlap,
    label_coverage_report,
)
from .load import TEXT_FEATURE_COLS, project_root, load_tcm_sd
from .preprocess import SyndromePreprocessor
from .split import make_leakage_safe_groups, partition_summary, split_groups_70_10_20


def run_pipeline(
    root: Path | None = None,
    random_state: int = 42,
    max_tfidf_features: int = 20000,
    select_k: int = 5000,
) -> dict:
    root = root or project_root()
    processed = root / "data" / "processed"
    artifacts = root / "artifacts" / "preprocess"
    processed.mkdir(parents=True, exist_ok=True)
    artifacts.mkdir(parents=True, exist_ok=True)

    df = load_tcm_sd(root)
    groups = make_leakage_safe_groups(df)
    parts = split_groups_70_10_20(df, groups=groups, random_state=random_state)

    overlap_report = assert_no_split_overlap(parts)
    leakage_report = assert_no_feature_label_leakage(TEXT_FEATURE_COLS)
    summary = partition_summary(parts)
    coverage = label_coverage_report(parts)

    # Persist row-level partitions for auditing (no model predictions)
    for name, frame in parts.items():
        keep = [
            "user_id",
            "case_fingerprint",
            "leakage_group",
            "partition",
            "norm_syndrome",
            "chief_complaint",
            "description",
            "detection",
        ]
        frame.loc[:, keep].to_parquet(processed / f"{name}_rows.parquet", index=False)

    pre = SyndromePreprocessor(
        max_tfidf_features=max_tfidf_features,
        select_k=select_k,
        random_state=random_state,
    )
    transformed = pre.fit_transform_parts(parts)
    pre.save(artifacts)

    matrices = {}
    for name, split in transformed.items():
        sparse.save_npz(processed / f"X_{name}.npz", split.X)
        joblib.dump(
            {
                "y": split.y,
                "y_labels": split.y_labels,
                "row_index": split.row_index,
                "n_unknown_labels": split.n_unknown_labels,
            },
            processed / f"y_{name}.joblib",
        )
        matrices[name] = {
            "X_shape": list(split.X.shape),
            "n_rows": int(split.X.shape[0]),
            "n_unknown_labels": split.n_unknown_labels,
            "nnz": int(split.X.nnz),
        }

    report = {
        "random_state": random_state,
        "requested_fractions": {"train": 0.70, "validation": 0.10, "test": 0.20},
        "partition_summary": summary.to_dict(orient="records"),
        "overlap_checks": overlap_report,
        "feature_leakage_checks": leakage_report,
        "labels_missing_from_train": int(coverage["missing_from_train"].sum()),
        "matrices": matrices,
        "notes": [
            "Preprocessor fitted on training partition only.",
            "Test partition transformed with frozen train statistics; not used for fitting.",
            "No machine-learning classifier was trained.",
            "Disease codes/names intentionally excluded from features to reduce leakage.",
        ],
    }
    (artifacts / "split_preprocess_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    summary.to_csv(artifacts / "partition_summary.csv", index=False)
    coverage.to_csv(artifacts / "label_coverage.csv", index=False)

    # Freeze a pointer that test must stay untouched by future training scripts
    (artifacts / "TEST_HOLD_OUT.txt").write_text(
        "The test partition in data/processed/*_test* must not be used for fitting "
        "or model selection. Validation may be used for tuning later; test only for "
        "final evaluation.\n",
        encoding="utf-8",
    )
    return report
