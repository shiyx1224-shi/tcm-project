"""Shared multiclass evaluation helpers for TCM-SD baselines."""

from __future__ import annotations

from typing import Any

import joblib
import numpy as np
from pathlib import Path
from scipy import sparse
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)

TASK_TYPE = "multiclass"  # TCM-SD: one norm_syndrome per record


def load_xy(processed: Path, split: str) -> tuple[sparse.csr_matrix, np.ndarray, np.ndarray]:
    X = sparse.load_npz(processed / f"X_{split}.npz").tocsr()
    payload = joblib.load(processed / f"y_{split}.joblib")
    y = np.asarray(payload["y"])
    labels = np.asarray(payload["y_labels"])
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
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "micro_f1": float(f1_score(y_true, y_pred, average="micro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "multilabel_metrics": {
            "applicable": False,
            "reason": "TCM-SD is single-label multiclass (one norm_syndrome per row).",
            "exact_match_accuracy": None,
            "hamming_loss": None,
        },
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=list(range(len(class_names))),
            target_names=class_names,
            zero_division=0,
            output_dict=True,
        ),
    }
    return metrics


COMPARISON_METRIC_COLUMNS = [
    "model",
    "task_type",
    "n_train",
    "n_validation",
    "n_features",
    "n_classes",
    "accuracy",
    "precision",
    "recall",
    "micro_f1",
    "macro_f1",
    "f1_weighted",
    "precision_macro",
    "recall_macro",
]
