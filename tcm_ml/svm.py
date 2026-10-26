"""Multiclass linear SVM for TCM-SD syndrome classification.

Uses LinearSVC on the same frozen train/validation matrices as Random Forest
and Logistic Regression. TCM-SD is single-label multiclass, so no multi-label
wrapper is applied. Kernel SVM is avoided here: RBF SVC is impractical on
~38k × 5k × 148 classes for this baseline slice.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.svm import LinearSVC

from .evaluation import TASK_TYPE, evaluate_multiclass, load_xy
from .load import TEXT_FEATURE_COLS, project_root
from .preprocess import SyndromePreprocessor


class SyndromeSVMPipeline:
    """End-to-end: clinical text fields → Linear SVM → syndrome label."""

    def __init__(self, preprocessor: SyndromePreprocessor, model: LinearSVC):
        self.preprocessor = preprocessor
        self.model = model
        self.task_type = TASK_TYPE

    def predict_records(self, records: list[dict[str, str]] | pd.DataFrame) -> list[dict[str, Any]]:
        frame = pd.DataFrame(records) if not isinstance(records, pd.DataFrame) else records.copy()
        for col in TEXT_FEATURE_COLS:
            if col not in frame.columns:
                frame[col] = ""
        X = self.preprocessor.transform_features(frame)
        pred_idx = self.model.predict(X)
        labels = self.preprocessor.label_encoder.inverse_transform(pred_idx)

        # LinearSVC has no predict_proba; use a softmax over decision scores as confidence
        confidence = None
        if hasattr(self.model, "decision_function"):
            scores = np.asarray(self.model.decision_function(X), dtype=np.float64)
            if scores.ndim == 1:
                # binary edge case
                confidence = 1.0 / (1.0 + np.exp(-scores))
            else:
                scores = scores - scores.max(axis=1, keepdims=True)
                exp = np.exp(scores)
                confidence = (exp / exp.sum(axis=1, keepdims=True))[
                    np.arange(len(pred_idx)), pred_idx
                ]

        outputs = []
        for i, label in enumerate(labels):
            item: dict[str, Any] = {
                "predicted_norm_syndrome": str(label),
                "predicted_class_index": int(pred_idx[i]),
            }
            if confidence is not None:
                item["confidence"] = float(confidence[i])
            outputs.append(item)
        return outputs

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, directory / "syndrome_svm_pipeline.joblib")

    @staticmethod
    def load(directory: Path) -> "SyndromeSVMPipeline":
        return joblib.load(Path(directory) / "syndrome_svm_pipeline.joblib")


def train_svm(
    root: Path | None = None,
    C: float = 1.0,
    max_iter: int = 5000,
    random_state: int = 42,
) -> dict[str, Any]:
    root = root or project_root()
    processed = root / "data" / "processed"
    pre_dir = root / "artifacts" / "preprocess"
    out_dir = root / "artifacts" / "models" / "svm"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not (processed / "X_train.npz").exists():
        raise FileNotFoundError(
            f"Missing processed matrices under {processed}. Run: python scripts/run_preprocess.py"
        )
    if not (pre_dir / "syndrome_preprocessor.joblib").exists():
        raise FileNotFoundError(
            f"Missing preprocessor under {pre_dir}. Run: python scripts/run_preprocess.py"
        )

    X_train, y_train, _ = load_xy(processed, "train")
    X_val, y_val, _ = load_xy(processed, "validation")

    # Sparse-native linear SVM (OvR multiclass). dual='auto' picks a stable formulation.
    model = LinearSVC(
        C=C,
        class_weight="balanced",
        dual="auto",
        max_iter=max_iter,
        random_state=random_state,
        tol=1e-3,
    )
    model.fit(X_train, y_train)

    preprocessor = SyndromePreprocessor.load(pre_dir)
    class_names = preprocessor.label_encoder.classes_.tolist()

    val_pred = model.predict(X_val)
    metrics = evaluate_multiclass(y_val, val_pred, class_names)
    metrics["model"] = {
        "type": "LinearSVC",
        "task_type": TASK_TYPE,
        "kernel": "linear",
        "C": C,
        "dual": "auto",
        "multi_class": "ovr",
        "class_weight": "balanced",
        "max_iter": max_iter,
        "random_state": random_state,
        "n_train": int(X_train.shape[0]),
        "n_validation": int(X_val.shape[0]),
        "n_features": int(X_train.shape[1]),
        "multi_label_wrapper": None,
        "multi_label_wrapper_reason": (
            "Not required: TCM-SD targets a single norm_syndrome per row (multiclass)."
        ),
        "note": "LinearSVC used instead of kernel SVC for tractable 148-class training.",
    }
    metrics["holdout_policy"] = {
        "validation_used_for": "initial model evaluation / traditional-ML ranking",
        "test_used": False,
        "note": "Same train/validation partitions as RF and LR; test untouched for model selection.",
        "shared_features_with": ["random_forest", "logistic_regression"],
    }

    joblib.dump(model, out_dir / "svm_model.joblib")
    pipeline = SyndromeSVMPipeline(preprocessor=preprocessor, model=model)
    pipeline.save(out_dir)

    (out_dir / "validation_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    summary = {k: v for k, v in metrics.items() if k != "classification_report"}
    (out_dir / "validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

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
