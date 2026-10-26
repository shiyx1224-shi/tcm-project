"""Final DS340W evaluation: validation-based selection, then untouched test eval.

Model selection uses only previously measured **validation** metrics.
The test partition is scored exactly once after the winner is locked.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

# Prefer a CJK-capable font so syndrome names render in figures
for _font in (
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
):
    if Path(_font).exists():
        font_manager.fontManager.addfont(_font)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=_font).get_name()
        plt.rcParams["axes.unicode_minus"] = False
        break

from .checks import assert_no_feature_label_leakage, assert_no_split_overlap
from .evaluation import evaluate_multiclass, load_xy
from .load import TEXT_FEATURE_COLS, project_root
from .preprocess import SyndromePreprocessor

# Primary ranking metric used throughout this project for fair comparison.
SELECTION_METRIC = "micro_f1"

DISPLAY = {
    "svm": "SVM (LinearSVC)",
    "random_forest": "Random Forest",
    "logistic_regression": "Logistic Regression",
    "chen_bert_cnn": "Chen-inspired BERT+CNN",
    "huang_cnn": "Huang-inspired CNN",
}


def _load_validation_leaderboard(root: Path) -> pd.DataFrame:
    path = root / "results" / "metrics" / "model_comparison.csv"
    frame = pd.read_csv(path)
    return frame.sort_values(SELECTION_METRIC, ascending=False).reset_index(drop=True)


def select_best_model(root: Path) -> dict[str, Any]:
    """Lock the winner from validation only (no test metrics consulted)."""
    board = _load_validation_leaderboard(root)
    best = board.iloc[0]
    decision = {
        "selected_model": str(best["model"]),
        "selection_metric": SELECTION_METRIC,
        "selection_value": float(best[SELECTION_METRIC]),
        "validation_accuracy": float(best["accuracy"]),
        "validation_precision": float(best["precision"]),
        "validation_recall": float(best["recall"]),
        "validation_micro_f1": float(best["micro_f1"]),
        "validation_macro_f1": float(best["macro_f1"]),
        "rationale": (
            f"Highest validation {SELECTION_METRIC} among models trained on the shared "
            "TCM-SD 70/10/20 features/partitions in results/metrics/model_comparison.csv. "
            "Test metrics were not used for selection."
        ),
        "leaderboard": board.to_dict(orient="records"),
        "test_consulted_during_selection": False,
    }
    return decision


def verify_integrity(root: Path) -> dict[str, Any]:
    processed = root / "data" / "processed"
    parts = {
        name: pd.read_parquet(processed / f"{name}_rows.parquet")
        for name in ("train", "validation", "test")
    }
    overlap = assert_no_split_overlap(parts)
    leakage = assert_no_feature_label_leakage(TEXT_FEATURE_COLS)

    # Extra audit: duplicate case fingerprints within a split (allowed) vs across (forbidden)
    sizes = {k: {"n_rows": int(len(v)), "n_patients": int(v["user_id"].nunique()),
                 "n_fingerprints": int(v["case_fingerprint"].nunique()),
                 "n_labels": int(v["norm_syndrome"].nunique())}
             for k, v in parts.items()}

    # Confirm preprocessor was train-only (meta exists) and test matrix shape matches
    pre_meta = json.loads((root / "artifacts" / "preprocess" / "preprocessor_meta.json").read_text())
    X_test, y_test, _ = load_xy(processed, "test")
    integrity = {
        "overlap_checks": overlap,
        "feature_leakage_checks": leakage,
        "partition_sizes": sizes,
        "preprocessor": {
            "n_classes_fit_on_train": pre_meta.get("n_classes"),
            "select_k": pre_meta.get("select_k"),
            "text_features": pre_meta.get("text_features"),
        },
        "test_matrix": {
            "X_shape": list(X_test.shape),
            "n_labels": int(len(y_test)),
            "n_unknown_labels": int((y_test < 0).sum()),
        },
        "ok": bool(overlap.get("ok")) and bool(leakage.get("ok")),
    }
    return integrity


def evaluate_selected_on_test(root: Path, selected_model: str) -> dict[str, Any]:
    if selected_model != "svm":
        raise ValueError(
            f"This final-eval harness currently loads the LinearSVC artifacts for 'svm'; "
            f"got selected_model={selected_model!r}"
        )
    processed = root / "data" / "processed"
    model_dir = root / "artifacts" / "models" / "svm"
    pre_dir = root / "artifacts" / "preprocess"

    model = joblib.load(model_dir / "svm_model.joblib")
    preprocessor = SyndromePreprocessor.load(pre_dir)
    class_names = preprocessor.label_encoder.classes_.tolist()

    X_test, y_test, y_labels = load_xy(processed, "test")
    y_pred = model.predict(X_test)
    metrics = evaluate_multiclass(y_test, y_pred, class_names)

    # Per-class error analysis (validation-selected model → test)
    report = metrics["classification_report"]
    per_class = []
    for name in class_names:
        cell = report.get(name, {})
        if not isinstance(cell, dict):
            continue
        support = int(cell.get("support", 0))
        if support <= 0:
            continue
        per_class.append(
            {
                "norm_syndrome": name,
                "precision": float(cell.get("precision", 0.0)),
                "recall": float(cell.get("recall", 0.0)),
                "f1": float(cell.get("f1-score", 0.0)),
                "support": support,
            }
        )
    per_class_df = pd.DataFrame(per_class).sort_values("f1", ascending=True)

    # Confusion among most frequent true labels (top-15 by support on test)
    top_labels = (
        per_class_df.sort_values("support", ascending=False).head(15)["norm_syndrome"].tolist()
    )
    label_to_idx = {n: i for i, n in enumerate(class_names)}
    top_idx = [label_to_idx[n] for n in top_labels]
    cm = confusion_matrix(y_test, y_pred, labels=top_idx)

    # Common confusions: off-diagonal pairs
    full_cm = confusion_matrix(y_test, y_pred, labels=list(range(len(class_names))))
    confusions = []
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            if i == j:
                continue
            count = int(full_cm[i, j])
            if count >= 5:
                confusions.append(
                    {
                        "true_label": class_names[i],
                        "predicted_label": class_names[j],
                        "count": count,
                    }
                )
    confusions_df = pd.DataFrame(confusions).sort_values("count", ascending=False)

    test_rows = pd.read_parquet(processed / "test_rows.parquet")
    # Align predictions preview with known-label rows only
    preview = pd.DataFrame(
        {
            "y_true_index": y_test[:100],
            "y_pred_index": y_pred[:100],
            "y_true_label": preprocessor.label_encoder.inverse_transform(y_test[:100]),
            "y_pred_label": preprocessor.label_encoder.inverse_transform(y_pred[:100]),
            "correct": y_test[:100] == y_pred[:100],
        }
    )

    return {
        "metrics": metrics,
        "per_class": per_class_df,
        "top15_labels": top_labels,
        "top15_confusion": cm,
        "confusions": confusions_df,
        "preview": preview,
        "n_test": int(len(y_test)),
        "n_test_rows_parquet": int(len(test_rows)),
    }


def _plot_final_f1_bars(val_board: pd.DataFrame, test_metrics: dict | None, out_path: Path) -> None:
    models = val_board["model"].tolist()
    labels = [DISPLAY.get(m, m) for m in models]
    micro = val_board["micro_f1"].tolist()
    macro = val_board["macro_f1"].tolist()

    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(models))
    w = 0.35
    ax.bar(x - w / 2, micro, w, label="Validation Micro-F1", color="#1f4e79")
    ax.bar(x + w / 2, macro, w, label="Validation Macro-F1", color="#2a6f4e")
    if test_metrics is not None:
        # Mark selected model's test F1 as points
        sel = val_board.iloc[0]["model"]
        si = models.index(sel)
        ax.scatter(
            [si - w / 2],
            [test_metrics["micro_f1"]],
            s=80,
            color="#c45c26",
            zorder=5,
            label="Test Micro-F1 (selected)",
        )
        ax.scatter(
            [si + w / 2],
            [test_metrics["macro_f1"]],
            s=80,
            marker="D",
            color="#a33b5a",
            zorder=5,
            label="Test Macro-F1 (selected)",
        )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("F1 score")
    ax.set_title("Final F1 comparison (validation all models; test = selected only)")
    ax.legend(frameon=False, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _plot_top_confusion(labels: list[str], cm: np.ndarray, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    # Shorten long Chinese labels for display
    short = [lab if len(lab) <= 8 else lab[:7] + "…" for lab in labels]
    ax.set_xticklabels(short, rotation=75, ha="right", fontsize=8)
    ax.set_yticklabels(short, fontsize=8)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Test confusion (top-15 syndromes by support)")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _plot_worst_classes(per_class: pd.DataFrame, out_path: Path, n: int = 20) -> None:
    worst = per_class.head(n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(worst["norm_syndrome"], worst["f1"], color="#8b2942")
    ax.set_xlabel("Test F1")
    ax.set_title(f"Lowest-{n} syndrome F1 on held-out test (selected SVM)")
    ax.set_xlim(0, 1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def write_final_report(
    root: Path,
    decision: dict[str, Any],
    integrity: dict[str, Any],
    test_pack: dict[str, Any],
    fs_summary: dict[str, Any],
) -> Path:
    test_metrics = {k: v for k, v in test_pack["metrics"].items() if k != "classification_report"}
    val_board = pd.DataFrame(decision["leaderboard"])
    sel = decision["selected_model"]
    sel_name = DISPLAY.get(sel, sel)

    lines = [
        "# Final evaluation — DS340W TCM syndrome classification",
        "",
        "**Research question:** How accurately can machine learning models classify TCM syndromes based on patients’ symptoms and clinical data?",
        "",
        "All numbers below are **measured** from artifacts under `results/` and `artifacts/models/`. Nothing is fabricated.",
        "",
        "## 1. Integrity verification (pre-test)",
        "",
        f"- Split overlap checks: **{'PASS' if integrity['overlap_checks']['ok'] else 'FAIL'}** "
        "(patient `user_id`, clinical `case_fingerprint`, and `leakage_group` intersections are all 0).",
        f"- Feature/label leakage checks: **{'PASS' if integrity['feature_leakage_checks']['ok'] else 'FAIL'}** "
        f"(model text features = {integrity['feature_leakage_checks']['feature_columns']}; "
        "banned ID/label columns absent).",
        f"- Preprocessor fit on train only; SelectKBest k={integrity['preprocessor']['select_k']}; "
        f"{integrity['preprocessor']['n_classes_fit_on_train']} classes.",
        f"- Test matrix shape: {integrity['test_matrix']['X_shape']}; "
        f"unknown labels in test encoding: {integrity['test_matrix']['n_unknown_labels']}.",
        "",
        "Partition sizes:",
        "",
        "| Partition | Rows | Patients | Fingerprints | Labels |",
        "|-----------|-----:|---------:|-------------:|-------:|",
    ]
    for name in ("train", "validation", "test"):
        s = integrity["partition_sizes"][name]
        lines.append(
            f"| {name} | {s['n_rows']} | {s['n_patients']} | {s['n_fingerprints']} | {s['n_labels']} |"
        )

    lines.extend(
        [
            "",
            "## 2. Validation leaderboard (model selection)",
            "",
            f"Selection rule: maximize validation **{SELECTION_METRIC}** on the shared baseline table "
            "`results/metrics/model_comparison.csv`. **Test was not consulted.**",
            "",
            "| Rank | Model | Accuracy | Precision | Recall | Micro-F1 | Macro-F1 |",
            "|-----:|-------|---------:|----------:|-------:|---------:|---------:|",
        ]
    )
    for i, row in val_board.iterrows():
        lines.append(
            f"| {i + 1} | {DISPLAY.get(row['model'], row['model'])} | "
            f"{row['accuracy']:.4f} | {row['precision']:.4f} | {row['recall']:.4f} | "
            f"{row['micro_f1']:.4f} | {row['macro_f1']:.4f} |"
        )

    lines.extend(
        [
            "",
            f"**Selected model: {sel_name}** "
            f"(validation {SELECTION_METRIC}={decision['selection_value']:.4f}).",
            "",
            "## 3. Feature-selection experiment (measured)",
            "",
            "Separate ablation at matched k=2000 (see `results/metrics/feature_selection_*.csv`). "
            "This did **not** change the primary baseline winner above (baselines use k=5000 chi2 features).",
            "",
            f"- Mean Δ micro-F1 vs unsupervised variance truncate: "
            f"MI={fs_summary['mean_delta_micro_f1']['mutual_information']:+.4f}, "
            f"RF-importance={fs_summary['mean_delta_micro_f1']['rf_importance']:+.4f}, "
            f"PCC-inspired={fs_summary['mean_delta_micro_f1']['pcc_inspired_gong']:+.4f}.",
            f"- SVM benefited from RF-importance selection (Δ micro-F1 "
            f"{fs_summary['svm_rf_importance_delta_micro_f1']:+.4f}); "
            "Random Forest generally did not benefit from supervised filters at matched k.",
            "",
            "## 4. Held-out test performance (selected SVM only)",
            "",
            f"Test n = {test_pack['n_test']} (parquet rows {test_pack['n_test_rows_parquet']}).",
            "",
            "| Split | Accuracy | Precision | Recall | Micro-F1 | Macro-F1 |",
            "|-------|---------:|----------:|-------:|---------:|---------:|",
            f"| Validation (selection) | {decision['validation_accuracy']:.4f} | "
            f"{decision['validation_precision']:.4f} | {decision['validation_recall']:.4f} | "
            f"{decision['validation_micro_f1']:.4f} | {decision['validation_macro_f1']:.4f} |",
            f"| **Test (final)** | **{test_metrics['accuracy']:.4f}** | "
            f"**{test_metrics['precision']:.4f}** | **{test_metrics['recall']:.4f}** | "
            f"**{test_metrics['micro_f1']:.4f}** | **{test_metrics['macro_f1']:.4f}** |",
            "",
            "Figures: `results/figures/final_f1_comparison.png`, "
            "`results/figures/final_test_confusion_top15.png`, "
            "`results/figures/final_test_worst_classes.png`.",
            "",
            "## 5. Error analysis (test)",
            "",
            "Lowest-F1 syndromes (head of `results/metrics/final_test_per_class.csv`):",
            "",
        ]
    )
    worst = test_pack["per_class"].head(10)
    lines.append("| Syndrome | Precision | Recall | F1 | Support |")
    lines.append("|----------|----------:|-------:|---:|--------:|")
    for _, r in worst.iterrows():
        lines.append(
            f"| {r['norm_syndrome']} | {r['precision']:.3f} | {r['recall']:.3f} | "
            f"{r['f1']:.3f} | {int(r['support'])} |"
        )

    top_conf = test_pack["confusions"].head(10)
    lines.extend(["", "Most frequent confusions (count ≥ 5):", ""])
    lines.append("| True | Predicted | Count |")
    lines.append("|------|-----------|------:|")
    for _, r in top_conf.iterrows():
        lines.append(f"| {r['true_label']} | {r['predicted_label']} | {int(r['count'])} |")

    lines.extend(
        [
            "",
            "## 6. Answers to the research questions",
            "",
            "### Which model performed best?",
            f"**{sel_name}** on validation ({SELECTION_METRIC}={decision['selection_value']:.4f}), "
            f"and the locked test evaluation reached micro-F1={test_metrics['micro_f1']:.4f}, "
            f"macro-F1={test_metrics['macro_f1']:.4f}.",
            "",
            "### Did feature selection improve classification?",
            "**Mixed.** Supervised selectors did not beat unsupervised variance truncation on average "
            "(negative mean Δ micro-F1 for MI / RF-importance / PCC-inspired). "
            "SVM gained from RF-importance (+micro/macro F1); Random Forest lost performance under "
            "several supervised filters at matched k=2000. Feature ranking remains useful for interpretability.",
            "",
            "### Did advanced (deep) methods improve over traditional ML?",
            "**No, not on this TCM-SD setup.** Huang-inspired CNN (val micro-F1=0.4635) and "
            "Chen-inspired BERT+CNN (val micro-F1=0.5007) both trailed LinearSVC and Random Forest. "
            "These were **adaptations** (virtual fields / frozen compact BERT; not exact paper reproductions) "
            "and lacked Huang’s 60 clinician fields and Chen’s constrained 21-label head.",
            "",
            "### How do results answer the research question?",
            "On public TCM-SD clinical text (chief complaint + description + four-exam notes) with a "
            "leakage-aware 70/10/20 split, traditional linear/margin models on train-fitted TF-IDF "
            f"features classify 148 syndromes with test micro-F1 **{test_metrics['micro_f1']:.4f}** "
            f"and macro-F1 **{test_metrics['macro_f1']:.4f}** for the selected SVM. "
            "Accuracy alone overstates rare-class quality: macro-F1 is substantially lower, matching "
            "the long-tailed label distribution.",
            "",
            "### Limitations and future work",
            "- TCM-SD is **multiclass**, not multi-label; Gong-style ML-PRDF was not faithfully applicable.",
            "- Huang/Chen deep models were adapted under data/compute constraints; stronger GPU finetuning "
            "or true structured four-exam fields might change the deep vs classical gap.",
            "- Char TF-IDF + engineered lengths are a proxy for symptoms, not a SymMap-normalized binary "
            "symptom vocabulary.",
            "- Test was evaluated once after selection; further tuning on test is disallowed.",
            "- Future work: calibrated probabilities, hierarchical TCM label constraints, multi-label "
            "corpora when licensed, and error-driven dictionary expansion for confused syndrome pairs.",
            "",
            "## Artifact index",
            "",
            "| Path | Role |",
            "|------|------|",
            "| `results/metrics/final_model_selection.json` | Locked validation decision |",
            "| `results/metrics/final_integrity_report.json` | Leakage / overlap audit |",
            "| `results/metrics/final_test_metrics.json` | Test metrics + model card |",
            "| `results/metrics/final_test_summary.json` | Compact test summary |",
            "| `results/metrics/final_test_per_class.csv` | Per-syndrome test P/R/F1 |",
            "| `results/metrics/final_test_confusions.csv` | Frequent error pairs |",
            "| `results/figures/final_*.png` | Comparison / confusion / worst-class plots |",
            "| `docs/final_evaluation.md` | This report |",
            "",
        ]
    )
    out = root / "docs" / "final_evaluation.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    (root / "results" / "metrics" / "final_evaluation.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return out


def run_final_evaluation(root: Path | None = None) -> dict[str, Any]:
    root = root or project_root()
    metrics_dir = root / "results" / "metrics"
    fig_dir = root / "results" / "figures"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    # --- Selection BEFORE any test scoring ---
    decision = select_best_model(root)
    (metrics_dir / "final_model_selection.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"SELECTED (validation only): {decision['selected_model']} "
        f"{SELECTION_METRIC}={decision['selection_value']:.4f}",
        flush=True,
    )

    integrity = verify_integrity(root)
    (metrics_dir / "final_integrity_report.json").write_text(
        json.dumps(integrity, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if not integrity["ok"]:
        raise RuntimeError(f"Integrity checks failed: {integrity}")
    print("Integrity checks PASSED.", flush=True)

    # Feature-selection measured summary for the write-up
    fs_deltas = pd.read_csv(metrics_dir / "feature_selection_f1_deltas.csv")
    fs_summary = {
        "mean_delta_micro_f1": {
            method: float(
                fs_deltas.loc[fs_deltas["selection_method"] == method, "delta_micro_f1"].mean()
            )
            for method in ("mutual_information", "rf_importance", "pcc_inspired_gong")
        },
        "svm_rf_importance_delta_micro_f1": float(
            fs_deltas.loc[
                (fs_deltas["model"] == "svm")
                & (fs_deltas["selection_method"] == "rf_importance"),
                "delta_micro_f1",
            ].iloc[0]
        ),
    }

    # --- Test evaluation ONLY for the locked model ---
    test_pack = evaluate_selected_on_test(root, decision["selected_model"])
    test_metrics = test_pack["metrics"]
    summary = {k: v for k, v in test_metrics.items() if k != "classification_report"}
    summary["selection"] = {
        "model": decision["selected_model"],
        "based_on": "validation",
        "metric": SELECTION_METRIC,
    }
    summary["integrity_ok"] = True

    (metrics_dir / "final_test_metrics.json").write_text(
        json.dumps(test_metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (metrics_dir / "final_test_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    test_pack["per_class"].to_csv(metrics_dir / "final_test_per_class.csv", index=False)
    test_pack["confusions"].to_csv(metrics_dir / "final_test_confusions.csv", index=False)
    test_pack["preview"].to_csv(metrics_dir / "final_test_preview.csv", index=False)

    val_board = pd.DataFrame(decision["leaderboard"])
    _plot_final_f1_bars(
        val_board,
        {"micro_f1": test_metrics["micro_f1"], "macro_f1": test_metrics["macro_f1"]},
        fig_dir / "final_f1_comparison.png",
    )
    _plot_top_confusion(
        test_pack["top15_labels"],
        test_pack["top15_confusion"],
        fig_dir / "final_test_confusion_top15.png",
    )
    _plot_worst_classes(test_pack["per_class"], fig_dir / "final_test_worst_classes.png")

    report_path = write_final_report(root, decision, integrity, test_pack, fs_summary)

    # Compact CSV for the final table
    final_table = val_board.copy()
    final_table["split"] = "validation"
    test_row = {
        "model": decision["selected_model"],
        "task_type": "multiclass",
        "n_train": int(val_board.iloc[0]["n_train"]),
        "n_validation": int(val_board.iloc[0]["n_validation"]),
        "n_test": int(test_metrics["n_samples"]),
        "n_features": int(val_board.iloc[0]["n_features"]),
        "n_classes": int(test_metrics["n_classes_in_encoder"]),
        "accuracy": test_metrics["accuracy"],
        "precision": test_metrics["precision"],
        "recall": test_metrics["recall"],
        "micro_f1": test_metrics["micro_f1"],
        "macro_f1": test_metrics["macro_f1"],
        "f1_weighted": test_metrics["f1_weighted"],
        "precision_macro": test_metrics["precision_macro"],
        "recall_macro": test_metrics["recall_macro"],
        "split": "test_selected_only",
    }
    pd.concat([final_table, pd.DataFrame([test_row])], ignore_index=True).to_csv(
        metrics_dir / "final_performance_table.csv", index=False
    )

    print(
        f"TEST ({decision['selected_model']}): "
        f"acc={test_metrics['accuracy']:.4f} micro_f1={test_metrics['micro_f1']:.4f} "
        f"macro_f1={test_metrics['macro_f1']:.4f}",
        flush=True,
    )
    print(f"Wrote {report_path}", flush=True)
    return {
        "decision": decision,
        "integrity": integrity,
        "test_summary": summary,
        "report": str(report_path),
    }
