"""Build a fair validation comparison table and chart across TCM-SD baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .evaluation import COMPARISON_METRIC_COLUMNS
from .load import project_root

MODEL_DIRS = {
    "random_forest": ("artifacts", "models", "random_forest"),
    "logistic_regression": ("artifacts", "models", "logistic_regression"),
    "svm": ("artifacts", "models", "svm"),
    "huang_cnn": ("artifacts", "models", "huang_cnn"),
}

DISPLAY_NAMES = {
    "random_forest": "Random Forest",
    "logistic_regression": "Logistic Regression",
    "svm": "SVM (LinearSVC)",
    "huang_cnn": "Huang-inspired CNN",
}


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
    rows = []
    for name, parts in MODEL_DIRS.items():
        directory = root.joinpath(*parts)
        if not (directory / "validation_summary.json").exists():
            continue
        summary = load_validation_summary(directory)
        rows.append(_row_from_summary(name, summary))
    if not rows:
        raise FileNotFoundError("No model validation_summary.json files found under artifacts/models/")
    frame = pd.DataFrame(rows, columns=COMPARISON_METRIC_COLUMNS)
    return frame.sort_values("accuracy", ascending=False).reset_index(drop=True)


def write_comparison_figure(frame: pd.DataFrame, out_path: Path) -> Path:
    """Grouped bar chart of core validation metrics for traditional ML baselines."""
    plot_metrics = [
        ("accuracy", "Accuracy"),
        ("precision", "Precision"),
        ("recall", "Recall"),
        ("micro_f1", "Micro-F1"),
        ("macro_f1", "Macro-F1"),
    ]
    # Stable display order (missing models skipped)
    preferred = ["random_forest", "logistic_regression", "svm", "huang_cnn"]
    models = [m for m in preferred if m in set(frame["model"])]
    models += [m for m in frame["model"] if m not in models]

    labels = [DISPLAY_NAMES.get(m, m) for m in models]
    x = range(len(plot_metrics))
    width = 0.18
    colors = {
        "random_forest": "#1f4e79",
        "logistic_regression": "#c45c26",
        "svm": "#2a6f4e",
        "huang_cnn": "#6b3fa0",
    }

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    for i, model in enumerate(models):
        row = frame.loc[frame["model"] == model].iloc[0]
        values = [float(row[key]) for key, _ in plot_metrics]
        offsets = [xi + (i - (len(models) - 1) / 2) * width for xi in x]
        bars = ax.bar(
            offsets,
            values,
            width=width,
            label=DISPLAY_NAMES.get(model, model),
            color=colors.get(model, f"C{i}"),
            edgecolor="white",
            linewidth=0.6,
        )
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.012,
                f"{val:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_xticks(list(x))
    ax.set_xticklabels([title for _, title in plot_metrics])
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Score")
    ax.set_title("TCM-SD validation comparison — traditional ML baselines")
    ax.legend(frameon=False, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.axhline(0, color="#333333", linewidth=0.8)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    return out_path


def write_model_comparison(root: Path | None = None) -> dict[str, Path]:
    root = root or project_root()
    out_dir = root / "results" / "metrics"
    fig_dir = root / "results" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    frame = build_comparison_frame(root)
    csv_path = out_dir / "model_comparison.csv"
    frame.to_csv(csv_path, index=False)

    fig_path = write_comparison_figure(frame, fig_dir / "model_comparison.png")

    best = frame.iloc[0]
    lines = [
        "# Model comparison (validation)",
        "",
        "Same frozen TCM-SD train/validation matrices and preprocessor for every model.",
        "Task type: multiclass (one `norm_syndrome` per record).",
        "**Test partition was not used for model selection or ranking.**",
        "",
        f"Primary ranking metric: validation accuracy. Best so far: **{best['model']}** "
        f"(accuracy={best['accuracy']:.4f}, micro_f1={best['micro_f1']:.4f}, "
        f"macro_f1={best['macro_f1']:.4f}).",
        "",
        "## Validation table",
        "",
        frame.to_markdown(index=False),
        "",
        f"![Validation metric comparison]({fig_path.relative_to(root).as_posix()})",
        "",
        "## Algorithm notes",
        "",
        "- **Random Forest** — non-linear ensemble of trees; `class_weight=balanced_subsample`.",
        "- **Logistic Regression** — linear multinomial classifier (`lbfgs`, balanced).",
        "- **SVM** — linear support-vector classifier (`LinearSVC`, OvR, balanced).",
        "- **Huang-inspired CNN** — AdaptedCrossFGCNN (cross network + FGCNN-style CNN); "
        "**not** an exact reproduction of Huang et al. 2022 (different data/fields/labels).",
        "",
    ]

    # Per-model one-liners ranked by accuracy
    lines.append("## Ranking (validation accuracy)")
    lines.append("")
    for i, row in frame.iterrows():
        lines.append(
            f"{i + 1}. **{DISPLAY_NAMES.get(row['model'], row['model'])}** — "
            f"accuracy={row['accuracy']:.4f}, precision={row['precision']:.4f}, "
            f"recall={row['recall']:.4f}, micro_f1={row['micro_f1']:.4f}, "
            f"macro_f1={row['macro_f1']:.4f}"
        )
    lines.append("")
    lines.append(
        f"**Conclusion:** Among the three traditional ML algorithms trained so far, "
        f"**{DISPLAY_NAMES.get(best['model'], best['model'])}** performs best on the "
        f"validation set and is the preferred baseline before any deep-learning work. "
        "The held-out test set remains sealed."
    )
    lines.append("")

    md_path = out_dir / "model_comparison.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"csv": csv_path, "markdown": md_path, "figure": fig_path}
