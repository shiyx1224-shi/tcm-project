"""Multiclass Logistic Regression for TCM-SD syndrome classification.

TCM-SD is single-label multiclass, so no multi-label wrapper (e.g.
MultiOutputClassifier / ClassifierChain) is used. sklearn's LogisticRegression
handles 148 classes with a multinomial objective.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from .evaluation import TASK_TYPE, evaluate_multiclass, load_xy
from .load import TEXT_FEATURE_COLS, project_root
from .preprocess import SyndromePreprocessor


class SyndromeLogisticRegressionPipeline:
    """End-to-end: clinical text fields → Logistic Regression → syndrome label."""

    def __init__(self, preprocessor: SyndromePreprocessor, model: LogisticRegression):
        self.preprocessor = preprocessor
        self.model = model
        self.task_type = TASK_TYPE

    def predict_records(self, records: list[dict[str, str]] | pd.DataFrame) -> list[dict[str, Any]]:
        frame = pd.DataFrame(records) if not isinstance(records, pd.DataFrame) else records.copy()
        for col in TEXT_FEATURE_COLS:
            if col not in frame.columns:
                frame[col] = ""
        X = self.preprocessor.transform_features(frame)
        # lbfgs model was fit on dense float32
        X_in = X.astype(np.float32).toarray() if hasattr(X, "toarray") else np.asarray(X)
        pred_idx = self.model.predict(X_in)
        proba = None
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(X_in)
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
        joblib.dump(self, directory / "syndrome_lr_pipeline.joblib")

    @staticmethod
    def load(directory: Path) -> "SyndromeLogisticRegressionPipeline":
        return joblib.load(Path(directory) / "syndrome_lr_pipeline.joblib")


def train_logistic_regression(
    root: Path | None = None,
    C: float = 1.0,
    max_iter: int = 500,
    random_state: int = 42,
) -> dict[str, Any]:
    root = root or project_root()
    processed = root / "data" / "processed"
    pre_dir = root / "artifacts" / "preprocess"
    out_dir = root / "artifacts" / "models" / "logistic_regression"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not (processed / "X_train.npz").exists():
        raise FileNotFoundError(
            f"Missing processed matrices under {processed}. Run: python scripts/run_preprocess.py"
        )
    if not (pre_dir / "syndrome_preprocessor.joblib").exists():
        raise FileNotFoundError(
            f"Missing preprocessor under {pre_dir}. Run: python scripts/run_preprocess.py"
        )

    # Same frozen matrices as Random Forest (no re-split / no re-fit of preprocessor)
    X_train, y_train, _ = load_xy(processed, "train")
    X_val, y_val, _ = load_xy(processed, "validation")

    # Dense float32 for lbfgs multinomial (same feature space as RF; saga was too slow
    # on 148-class × 5k features). No multi-label wrapper — TCM-SD is multiclass.
    X_train_dense = X_train.astype(np.float32).toarray()
    del X_train
    X_val_dense = X_val.astype(np.float32).toarray()
    del X_val

    model = LogisticRegression(
        C=C,
        solver="lbfgs",
        class_weight="balanced",
        max_iter=max_iter,
        random_state=random_state,
        tol=1e-3,
    )
    model.fit(X_train_dense, y_train)
    n_train, n_features = X_train_dense.shape
    del X_train_dense

    preprocessor = SyndromePreprocessor.load(pre_dir)
    class_names = preprocessor.label_encoder.classes_.tolist()

    val_pred = model.predict(X_val_dense)
    metrics = evaluate_multiclass(y_val, val_pred, class_names)
    metrics["model"] = {
        "type": "LogisticRegression",
        "task_type": TASK_TYPE,
        "C": C,
        "solver": "lbfgs",
        "multi_class": "multinomial (sklearn default)",
        "class_weight": "balanced",
        "max_iter": max_iter,
        "random_state": random_state,
        "n_train": int(n_train),
        "n_validation": int(X_val_dense.shape[0]),
        "n_features": int(n_features),
        "multi_label_wrapper": None,
        "multi_label_wrapper_reason": (
            "Not required: TCM-SD targets a single norm_syndrome per row (multiclass)."
        ),
    }
    metrics["holdout_policy"] = {
        "validation_used_for": "initial model evaluation",
        "test_used": False,
        "note": "Same train/validation partitions as Random Forest; test untouched.",
        "shared_features_with": "random_forest",
    }
    del X_val_dense

    joblib.dump(model, out_dir / "logistic_regression_model.joblib")
    pipeline = SyndromeLogisticRegressionPipeline(preprocessor=preprocessor, model=model)
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
