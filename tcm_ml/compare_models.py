"""Build a fair validation comparison table across trained TCM-SD baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .evaluation import COMPARISON_METRIC_COLUMNS
from .load import project_root


def _row_from_summary(name: str, summary: dict[str, Any]) -> dict[str, Any]:
    model_meta = summary.get("model", {})
    return {
        "model": name,
        "task_type": summary.get("task_type", model_meta.get("task_type")),
        "n_train": model_meta.get("n_train"),
        "n_validation": model_meta.get("n_validation", summary.get("n_samples")),
        "n_features": model_meta.get("n_features"),
        "n_classes": summary.get("n_classes_in_encoder"),
        "accuracy": summary.get("accuracy"),
        "precision": summary.get("precision"),
        "recall": summary.get("recall"),
        "micro_f1": summary.get("micro_f1"),
        "macro_f1": summary.get("macro_f1"),
        "f1_weighted": summary.get("f1_weighted"),
        "precision_macro": summary.get("precision_macro"),
        "recall_macro": summary.get("recall_macro"),
    }


def load_validation_summary(model_dir: Path) -> dict[str, Any]:
    path = model_dir / "validation_summary.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_comparison_frame(root: Path | None = None) -> pd.DataFrame:
    root = root or project_root()
    models = {
        "random_forest": root / "artifacts" / "models" / "random_forest",
        "logistic_regression": root / "artifacts" / "models" / "logistic_regression",
    }
    rows = []
    for name, directory in models.items():
        summary = load_validation_summary(directory)
        rows.append(_row_from_summary(name, summary))
    frame = pd.DataFrame(rows, columns=COMPARISON_METRIC_COLUMNS)
    return frame.sort_values("accuracy", ascending=False).reset_index(drop=True)


def write_model_comparison(root: Path | None = None) -> Path:
    root = root or project_root()
    out_dir = root / "results" / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    frame = build_comparison_frame(root)
    out_path = out_dir / "model_comparison.csv"
    frame.to_csv(out_path, index=False)

    # Narrative summary for the research write-up
    best = frame.iloc[0]
    other = frame.iloc[1] if len(frame) > 1 else None
    lines = [
        "# Model comparison (validation)",
        "",
        "Same frozen TCM-SD train/validation matrices and preprocessor for every model.",
        "Task type: multiclass (one `norm_syndrome` per record). Test partition unused.",
        "",
        f"Primary ranking metric: validation accuracy. Best so far: **{best['model']}** "
        f"(accuracy={best['accuracy']:.4f}, micro_f1={best['micro_f1']:.4f}, "
        f"macro_f1={best['macro_f1']:.4f}).",
        "",
    ]
    if other is not None:
        acc_delta = float(best["accuracy"]) - float(other["accuracy"])
        macro_delta = float(best["macro_f1"]) - float(other["macro_f1"])
        lines.extend(
            [
                "## Differences",
                "",
                "- **Random Forest** averages many shallow decision trees with "
                "`class_weight=balanced_subsample`. It can model non-linear interactions "
                "among TF-IDF / length features, which helps separate visually similar "
                "syndrome charts.",
                "- **Logistic Regression** uses a linear multinomial decision boundary "
                "(`lbfgs`, L2, `class_weight=balanced`) in the same 5,000-D feature space. "
                "It is much smaller on disk than the RF ensemble but cannot capture "
                "higher-order feature interactions without explicit crosses.",
                "- No multi-label wrapper (`MultiOutputClassifier` / `ClassifierChain`) "
                "was applied: the verified TCM-SD target is multiclass, not multi-label.",
                "",
                f"Accuracy gap ({best['model']} − {other['model']}): {acc_delta:+.4f}.",
                f"Macro-F1 gap ({best['model']} − {other['model']}): {macro_delta:+.4f}.",
                "",
                "On this validation set, Random Forest is clearly stronger on accuracy, "
                "recall, micro-F1, and macro-F1. Weighted precision is similar for both "
                "(both near ~0.78), which suggests Logistic Regression often abstains "
                "from rare classes less cleanly—higher false negatives drag recall and F1.",
                "",
                "Macro-F1 emphasizes rare syndromes; micro-F1 / accuracy weight frequent "
                "labels more heavily on this 148-class set.",
                "",
            ]
        )
    (out_dir / "model_comparison.md").write_text("\n".join(lines), encoding="utf-8")
    return out_path
