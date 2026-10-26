"""Multiclass Random Forest for TCM-SD syndrome classification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)

from .load import TEXT_FEATURE_COLS, project_root
from .preprocess import SyndromePreprocessor

TASK_TYPE = "multiclass"  # TCM-SD: one norm_syndrome per record


@dataclass
class RFArtifacts:
    directory: Path
    model_path: Path
    pipeline_path: Path
    metrics_path: Path


def _load_xy(processed: Path, split: str) -> tuple[sparse.csr_matrix, np.ndarray, np.ndarray]:
    X = sparse.load_npz(processed / f"X_{split}.npz").tocsr()
    payload = joblib.load(processed / f"y_{split}.joblib")
    y = np.asarray(payload["y"])
    labels = np.asarray(payload["y_labels"])
    # Drop any unknown-label rows (should be 0 for our split)
    keep = y >= 0
    return X[keep], y[keep], labels[keep]


def evaluate_multiclass(y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str]) -> dict[str, Any]:
    metrics = {
        "task_type": TASK_TYPE,
        "n_samples": int(len(y_true)),
        "n_classes_in_encoder": len(class_names),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_weighted": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_weighted": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_micro": float(f1_score(y_true, y_pred, average="micro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        # Explicit aliases matching the assignment wording
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "micro_f1": float(f1_score(y_true, y_pred, average="micro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }
    # Multi-label metrics are not applicable; record that clearly
    metrics["multilabel_metrics"] = {
        "applicable": False,
        "reason": "TCM-SD is single-label multiclass (one norm_syndrome per row).",
        "exact_match_accuracy": None,
        "hamming_loss": None,
    }
    metrics["classification_report"] = classification_report(
        y_true,
        y_pred,
        labels=list(range(len(class_names))),
        target_names=class_names,
        zero_division=0,
        output_dict=True,
    )
    return metrics


class SyndromeRandomForestPipeline:
    """End-to-end: clinical text fields → Random Forest → syndrome label."""

    def __init__(self, preprocessor: SyndromePreprocessor, model: RandomForestClassifier):
        self.preprocessor = preprocessor
        self.model = model
        self.task_type = TASK_TYPE

    def predict_records(self, records: list[dict[str, str]] | pd.DataFrame) -> list[dict[str, Any]]:
        frame = pd.DataFrame(records) if not isinstance(records, pd.DataFrame) else records.copy()
        for col in TEXT_FEATURE_COLS:
            if col not in frame.columns:
                frame[col] = ""
        X = self.preprocessor.transform_features(frame)
        # RandomForest expects dense arrays
        X_dense = X.toarray()
        pred_idx = self.model.predict(X_dense)
        proba = None
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(X_dense)
        labels = self.preprocessor.label_encoder.inverse_transform(pred_idx)
        outputs = []
        for i, label in enumerate(labels):
            item: dict[str, Any] = {
                "predicted_norm_syndrome": str(label),
                "predicted_class_index": int(pred_idx[i]),
            }
            if proba is not None:
                item["confidence"] = float(proba[i, pred_idx[i]])
            outputs.append(item)
        return outputs

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, directory / "syndrome_rf_pipeline.joblib")

    @staticmethod
    def load(directory: Path) -> "SyndromeRandomForestPipeline":
        return joblib.load(Path(directory) / "syndrome_rf_pipeline.joblib")


def train_random_forest(
    root: Path | None = None,
    n_estimators: int = 100,
    max_depth: int | None = 40,
    random_state: int = 42,
    n_jobs: int = 4,
) -> dict[str, Any]:
    root = root or project_root()
    processed = root / "data" / "processed"
    pre_dir = root / "artifacts" / "preprocess"
    out_dir = root / "artifacts" / "models" / "random_forest"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not (processed / "X_train.npz").exists():
        raise FileNotFoundError(
            f"Missing processed matrices under {processed}. Run: python scripts/run_preprocess.py"
        )
    if not (pre_dir / "syndrome_preprocessor.joblib").exists():
        raise FileNotFoundError(
            f"Missing preprocessor under {pre_dir}. Run: python scripts/run_preprocess.py"
        )

    X_train, y_train, _ = _load_xy(processed, "train")
    X_val, y_val, _ = _load_xy(processed, "validation")

    # Dense conversion required by RandomForestClassifier; free sparse copies after
    X_train_dense = X_train.astype(np.float32).toarray()
    del X_train
    X_val_dense = X_val.astype(np.float32).toarray()
    del X_val

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=n_jobs,
        class_weight="balanced_subsample",
        min_samples_leaf=2,
    )
    model.fit(X_train_dense, y_train)
    del X_train_dense

    preprocessor = SyndromePreprocessor.load(pre_dir)
    class_names = preprocessor.label_encoder.classes_.tolist()

    val_pred = model.predict(X_val_dense)
    metrics = evaluate_multiclass(y_val, val_pred, class_names)
    metrics["model"] = {
        "type": "RandomForestClassifier",
        "task_type": TASK_TYPE,
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "random_state": random_state,
        "n_jobs": n_jobs,
        "n_train": int(len(y_train)),
        "n_validation": int(X_val_dense.shape[0]),
        "n_features": int(X_val_dense.shape[1]),
        "class_weight": "balanced_subsample",
        "min_samples_leaf": 2,
    }
    metrics["holdout_policy"] = {
        "validation_used_for": "initial model evaluation",
        "test_used": False,
        "note": "Test partition remains untouched until final evaluation.",
    }
    del X_val_dense

    joblib.dump(model, out_dir / "random_forest_model.joblib")
    pipeline = SyndromeRandomForestPipeline(preprocessor=preprocessor, model=model)
    pipeline.save(out_dir)

    (out_dir / "validation_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # Compact human-readable summary without the huge per-class report dump twice
    summary = {k: v for k, v in metrics.items() if k != "classification_report"}
    (out_dir / "validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Save a few validation predictions for spot checks
    preview = pd.DataFrame(
        {
            "y_true_index": y_val[:50],
            "y_pred_index": val_pred[:50],
            "y_true_label": preprocessor.label_encoder.inverse_transform(y_val[:50]),
            "y_pred_label": preprocessor.label_encoder.inverse_transform(val_pred[:50]),
        }
    )
    preview.to_csv(out_dir / "validation_preview.csv", index=False)

    return {
        "artifacts": str(out_dir),
        "validation_summary": summary,
    }
