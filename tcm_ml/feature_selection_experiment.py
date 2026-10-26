"""Feature-selection ablation for TCM-SD traditional ML baselines.

Leakage policy
--------------
Selectors are fit on the **training partition only**. Validation and test
labels never enter ranking, scoring, or threshold choice.

Parent-paper adaptations (documented accurately)
-----------------------------------------------
- Gong et al. 2023 (PCC-MLRF): full multi-label ReliefF with Pearson neighbor
  weights is not run (TCM-SD is multiclass; ReliefF on ~38k×20k is intractable
  here). We implement a **PCC-inspired filter**: rank features by mean absolute
  Pearson correlation with one-hot syndrome indicators on a training subsample.
  This keeps Gong's Pearson-correlation idea as a supervised filter, not the
  full ML-ReliefF / PCC-MLRF pipeline.
- Huang et al. 2022: uses TCM field segmentation + learned cross features, not
  a classic filter. Not reimplemented as deep Cross-FGCNN (out of scope).
- Chen et al. 2024: no classic filter (BERT embeddings + correlation viz).
  Mutual-information / importance charts play a similar interpretability role.

"Without feature selection" uses an **unsupervised** variance ranking truncated
to the same k as supervised methods so dimensionality is matched and only the
*supervision* of selection differs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from .evaluation import evaluate_multiclass
from .load import TARGET_COL, TEXT_FEATURE_COLS, project_root
from .preprocess import SyndromePreprocessor, _categorical_frame, _combine_text, _numeric_frame

METHOD_ORDER = [
    "no_supervised_fs",
    "mutual_information",
    "rf_importance",
    "pcc_inspired_gong",
]

METHOD_LABELS = {
    "no_supervised_fs": "No supervised FS\n(variance truncate)",
    "mutual_information": "Mutual information",
    "rf_importance": "RF / ExtraTrees importance",
    "pcc_inspired_gong": "PCC-inspired (Gong adapt.)",
}

MODEL_ORDER = ["random_forest", "logistic_regression", "svm"]
MODEL_LABELS = {
    "random_forest": "Random Forest",
    "logistic_regression": "Logistic Regression",
    "svm": "SVM (LinearSVC)",
}


def _ensure_dirs(root: Path) -> dict[str, Path]:
    paths = {
        "exp": root / "artifacts" / "feature_selection",
        "metrics": root / "results" / "metrics",
        "figures": root / "results" / "figures",
        "docs": root / "docs",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def transform_unselected(preprocessor: SyndromePreprocessor, frame: pd.DataFrame) -> sparse.csr_matrix:
    """Apply fitted TF-IDF / scaler / one-hot **without** SelectKBest."""
    if not preprocessor.fitted_:
        raise RuntimeError("Preprocessor must be fitted")
    clean = frame.copy()
    for col in TEXT_FEATURE_COLS:
        if col not in clean.columns:
            clean[col] = ""
        clean[col] = clean[col].fillna("").astype(str)
    text = _combine_text(clean)
    numeric = _numeric_frame(clean).fillna(0.0)
    categorical = _categorical_frame(clean).fillna("missing")
    X_text = preprocessor.tfidf.transform(text)
    X_num = preprocessor.scaler.transform(numeric)
    X_cat = preprocessor.onehot.transform(categorical)
    return sparse.hstack([X_text, sparse.csr_matrix(X_num), X_cat], format="csr")


def feature_names(preprocessor: SyndromePreprocessor) -> list[str]:
    names: list[str] = []
    # Char n-grams — use opaque ids when get_feature_names_out is huge
    n_tfidf = len(preprocessor.tfidf.vocabulary_)
    names.extend([f"tfidf_{i}" for i in range(n_tfidf)])
    num_names = [
        f"{c}_char_len" for c in TEXT_FEATURE_COLS
    ] + [
        f"{c}_token_approx" for c in TEXT_FEATURE_COLS
    ] + ["total_char_len"]
    names.extend(num_names)
    try:
        cat_names = preprocessor.onehot.get_feature_names_out(["description_length_bin"]).tolist()
    except Exception:
        cat_names = [f"cat_{i}" for i in range(preprocessor.onehot.transform(pd.DataFrame({"description_length_bin": ["short"]})).shape[1])]
    names.extend(cat_names)
    return names


def _variance_scores(X: sparse.csr_matrix) -> np.ndarray:
    """Unsupervised per-feature variance (train X only; no labels)."""
    X = X.tocsr().astype(np.float64)
    # E[x^2] - (E[x])^2 for sparse columns
    mean = np.asarray(X.mean(axis=0)).ravel()
    mean_sq = np.asarray(X.power(2).mean(axis=0)).ravel()
    return np.maximum(mean_sq - mean**2, 0.0)


def _entropy_from_counts(counts: np.ndarray) -> float:
    total = counts.sum()
    if total <= 0:
        return 0.0
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p)).sum())


def _mutual_info_scores(
    X: sparse.csr_matrix,
    y: np.ndarray,
    random_state: int,
    candidate_mask: np.ndarray,
) -> np.ndarray:
    """Vectorized discrete MI between binarized feature presence and labels.

    Continuous dense `mutual_info_classif` is intractable at this scale.
    Binarize TF-IDF presence and compute MI(X_j; Y) = H(Y) - H(Y|X_j) using
    one-hot label indicators × sparse presence counts.
    """
    rng = np.random.default_rng(random_state)
    n = X.shape[0]
    sample_n = min(15000, n)
    idx = rng.choice(n, size=sample_n, replace=False)
    cand = np.where(candidate_mask)[0]
    X_bin = (X[idx][:, cand] > 0).astype(np.float64).tocsr()
    y_s = y[idx]
    classes, y_codes = np.unique(y_s, return_inverse=True)
    n_classes = len(classes)
    y_oh = np.zeros((sample_n, n_classes), dtype=np.float64)
    y_oh[np.arange(sample_n), y_codes] = 1.0
    hy = _entropy_from_counts(y_oh.sum(axis=0))

    # counts_1[f, c] = #samples with feature f present and class c
    counts_1 = (X_bin.T @ y_oh)  # (n_cand, n_classes)
    n1 = np.asarray(X_bin.sum(axis=0)).ravel()  # (n_cand,)
    class_totals = y_oh.sum(axis=0)
    counts_0 = class_totals - counts_1
    n0 = sample_n - n1

    def _row_entropies(counts: np.ndarray, row_n: np.ndarray) -> np.ndarray:
        # counts: (n_feat, n_classes), row_n: (n_feat,)
        with np.errstate(divide="ignore", invalid="ignore"):
            probs = np.divide(counts, row_n[:, None], out=np.zeros_like(counts), where=row_n[:, None] > 0)
        probs = np.clip(probs, 0, 1)
        logp = np.zeros_like(probs)
        mask = probs > 0
        logp[mask] = np.log2(probs[mask])
        return -(probs * logp).sum(axis=1)

    h1 = _row_entropies(counts_1, n1)
    h0 = _row_entropies(counts_0, n0)
    h_cond = np.zeros(len(cand), dtype=np.float64)
    pos = n1 > 0
    neg = n0 > 0
    h_cond[pos] += (n1[pos] / sample_n) * h1[pos]
    h_cond[neg] += (n0[neg] / sample_n) * h0[neg]
    scores_cand = np.maximum(hy - h_cond, 0.0)

    scores = np.zeros(X.shape[1], dtype=np.float64)
    scores[cand] = scores_cand
    return scores


def _rf_importance_scores(
    X: sparse.csr_matrix,
    y: np.ndarray,
    random_state: int,
    candidate_mask: np.ndarray,
) -> np.ndarray:
    """Model-based importance via ExtraTrees on variance-prefiltered candidates."""
    rng = np.random.default_rng(random_state)
    n = X.shape[0]
    sample_n = min(10000, n)
    idx = rng.choice(n, size=sample_n, replace=False)
    cand = np.where(candidate_mask)[0]
    X_dense = X[idx][:, cand].astype(np.float32).toarray()
    model = ExtraTreesClassifier(
        n_estimators=60,
        max_depth=22,
        min_samples_leaf=2,
        max_features="sqrt",
        n_jobs=4,
        random_state=random_state,
        class_weight="balanced_subsample",
    )
    model.fit(X_dense, y[idx])
    scores = np.zeros(X.shape[1], dtype=np.float64)
    scores[cand] = np.asarray(model.feature_importances_, dtype=np.float64)
    return scores


def _pcc_inspired_scores(
    X: sparse.csr_matrix,
    y: np.ndarray,
    random_state: int,
    candidate_mask: np.ndarray,
) -> np.ndarray:
    """Gong-inspired Pearson filter (multiclass adaptation; not full PCC-MLRF).

    For each candidate feature, compute mean |Pearson r| against one-hot syndrome
    columns on a training subsample. Higher = more syndrome-informative.
    """
    rng = np.random.default_rng(random_state)
    n = X.shape[0]
    sample_n = min(10000, n)
    idx = rng.choice(n, size=sample_n, replace=False)
    cand = np.where(candidate_mask)[0]
    X_s = X[idx][:, cand].astype(np.float64).tocsc()
    y_s = y[idx]
    classes = np.unique(y_s)
    mean = np.asarray(X_s.mean(axis=0)).ravel()
    y_oh = np.zeros((sample_n, len(classes)), dtype=np.float64)
    class_to_col = {c: i for i, c in enumerate(classes)}
    for i, lab in enumerate(y_s):
        y_oh[i, class_to_col[lab]] = 1.0
    y_mean = y_oh.mean(axis=0)
    y_std = y_oh.std(axis=0)
    y_std[y_std < 1e-12] = 1.0
    y_z = (y_oh - y_mean) / y_std

    n_cand = X_s.shape[1]
    cand_scores = np.zeros(n_cand, dtype=np.float64)
    block = 512
    for start in range(0, n_cand, block):
        end = min(start + block, n_cand)
        block_mat = X_s[:, start:end].toarray()
        b_mean = mean[start:end]
        b_std = block_mat.std(axis=0)
        b_std[b_std < 1e-12] = 1.0
        x_z = (block_mat - b_mean) / b_std
        corr = np.abs(x_z.T @ y_z) / max(sample_n - 1, 1)
        cand_scores[start:end] = corr.mean(axis=1)
    scores = np.zeros(X.shape[1], dtype=np.float64)
    scores[cand] = cand_scores
    return scores


def top_k_mask(scores: np.ndarray, k: int) -> np.ndarray:
    k = min(k, scores.shape[0])
    idx = np.argpartition(scores, -k)[-k:]
    mask = np.zeros(scores.shape[0], dtype=bool)
    mask[idx] = True
    return mask


def apply_mask(X: sparse.csr_matrix, mask: np.ndarray) -> sparse.csr_matrix:
    return X[:, mask].tocsr()


def _train_predict(
    model_name: str,
    X_train: sparse.csr_matrix,
    y_train: np.ndarray,
    X_val: sparse.csr_matrix,
    random_state: int,
) -> np.ndarray:
    if model_name == "logistic_regression":
        clf = LogisticRegression(
            C=1.0,
            solver="lbfgs",
            class_weight="balanced",
            max_iter=400,
            random_state=random_state,
            tol=1e-3,
        )
        Xtr = X_train.astype(np.float32).toarray()
        Xva = X_val.astype(np.float32).toarray()
        clf.fit(Xtr, y_train)
        return clf.predict(Xva)

    if model_name == "svm":
        clf = LinearSVC(
            C=1.0,
            class_weight="balanced",
            dual="auto",
            max_iter=4000,
            random_state=random_state,
            tol=1e-3,
        )
        clf.fit(X_train, y_train)
        return clf.predict(X_val)

    if model_name == "random_forest":
        clf = RandomForestClassifier(
            n_estimators=80,
            max_depth=36,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=4,
            random_state=random_state,
        )
        Xtr = X_train.astype(np.float32).toarray()
        Xva = X_val.astype(np.float32).toarray()
        clf.fit(Xtr, y_train)
        return clf.predict(Xva)

    raise ValueError(model_name)


def _plot_importance(
    names: list[str],
    scores: np.ndarray,
    mask: np.ndarray,
    title: str,
    out_path: Path,
    top_n: int = 30,
) -> None:
    selected_idx = np.where(mask)[0]
    selected_scores = scores[selected_idx]
    order = np.argsort(selected_scores)[::-1][:top_n]
    top_idx = selected_idx[order]
    top_scores = scores[top_idx]
    top_names = [names[i] if i < len(names) else f"f{i}" for i in top_idx]

    fig, ax = plt.subplots(figsize=(9, 7))
    y_pos = np.arange(len(top_names))[::-1]
    ax.barh(y_pos, top_scores, color="#1f4e79", height=0.75)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_names, fontsize=8)
    ax.set_xlabel("Selection score (train only)")
    ax.set_title(title)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _plot_f1_heatmap(delta: pd.DataFrame, out_path: Path) -> None:
    metrics = ["delta_accuracy", "delta_micro_f1", "delta_macro_f1"]
    labels = ["Δ Accuracy", "Δ Micro-F1", "Δ Macro-F1"]
    mat = delta.set_index("model")[metrics].loc[MODEL_ORDER].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    im = ax.imshow(mat, cmap="RdBu", vmin=-0.15, vmax=0.15, aspect="auto")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticks(range(len(MODEL_ORDER)))
    ax.set_yticklabels([MODEL_LABELS[m] for m in MODEL_ORDER])
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, f"{mat[i, j]:+.3f}", ha="center", va="center", fontsize=10)
    ax.set_title("Best supervised FS − no supervised FS (validation)")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _plot_grouped_comparison(results: pd.DataFrame, out_path: Path) -> None:
    metrics = [("accuracy", "Accuracy"), ("micro_f1", "Micro-F1"), ("macro_f1", "Macro-F1")]
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2), sharey=True)
    x = np.arange(len(MODEL_ORDER))
    width = 0.18
    colors = {
        "no_supervised_fs": "#8a8a8a",
        "mutual_information": "#c45c26",
        "rf_importance": "#1f4e79",
        "pcc_inspired_gong": "#2a6f4e",
    }
    for ax, (key, title) in zip(axes, metrics):
        for i, method in enumerate(METHOD_ORDER):
            vals = []
            for model in MODEL_ORDER:
                row = results[(results["model"] == model) & (results["selection_method"] == method)]
                vals.append(float(row.iloc[0][key]) if len(row) else np.nan)
            ax.bar(
                x + (i - 1.5) * width,
                vals,
                width=width,
                label=METHOD_LABELS[method].replace("\n", " "),
                color=colors[method],
            )
        ax.set_xticks(x)
        ax.set_xticklabels([MODEL_LABELS[m] for m in MODEL_ORDER], rotation=15, ha="right")
        ax.set_title(title)
        ax.set_ylim(0, 1.0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.08))
    fig.suptitle("Feature selection × classifier (validation)", y=1.12, fontsize=13)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def run_feature_selection_experiment(
    root: Path | None = None,
    k: int = 2000,
    random_state: int = 42,
) -> dict[str, Any]:
    root = root or project_root()
    paths = _ensure_dirs(root)
    processed = root / "data" / "processed"
    pre_dir = root / "artifacts" / "preprocess"

    train_rows = pd.read_parquet(processed / "train_rows.parquet")
    val_rows = pd.read_parquet(processed / "validation_rows.parquet")
    preprocessor = SyndromePreprocessor.load(pre_dir)
    class_names = preprocessor.label_encoder.classes_.tolist()

    # Encode labels with the frozen train encoder (no val/test refit)
    y_train = preprocessor.label_encoder.transform(train_rows[TARGET_COL].astype(str))
    known = set(preprocessor.label_encoder.classes_)
    val_mask = val_rows[TARGET_COL].astype(str).isin(known)
    val_rows = val_rows.loc[val_mask].copy()
    y_val = preprocessor.label_encoder.transform(val_rows[TARGET_COL].astype(str))

    print("Building unselected feature matrices (train-fitted transformers only)...", flush=True)
    X_train_full = transform_unselected(preprocessor, train_rows)
    X_val_full = transform_unselected(preprocessor, val_rows)
    names = feature_names(preprocessor)
    if len(names) != X_train_full.shape[1]:
        names = [f"f{i}" for i in range(X_train_full.shape[1])]

    print(f"Pool shape train={X_train_full.shape}, val={X_val_full.shape}, k={k}", flush=True)

    # Unsupervised variance prefilter (train X only) shrinks the candidate set for
    # expensive supervised scorers. Labels are still unused at this step.
    variance_all = _variance_scores(X_train_full)
    candidate_n = min(6000, X_train_full.shape[1])
    candidate_mask = top_k_mask(variance_all, candidate_n)
    print(f"Variance prefilter candidates: {candidate_mask.sum()} (no labels used)", flush=True)

    scorers: dict[str, Callable[[], np.ndarray]] = {
        "no_supervised_fs": lambda: variance_all,
        "mutual_information": lambda: _mutual_info_scores(
            X_train_full, y_train, random_state, candidate_mask
        ),
        "rf_importance": lambda: _rf_importance_scores(
            X_train_full, y_train, random_state, candidate_mask
        ),
        "pcc_inspired_gong": lambda: _pcc_inspired_scores(
            X_train_full, y_train, random_state, candidate_mask
        ),
    }

    selection_meta = {}
    masks: dict[str, np.ndarray] = {}
    score_tables = []

    for method, scorer in scorers.items():
        print(f"Scoring features: {method}", flush=True)
        scores = scorer()
        print(f"  done {method}", flush=True)
        mask = top_k_mask(scores, k)
        masks[method] = mask
        uses_labels = method != "no_supervised_fs"
        selection_meta[method] = {
            "uses_train_labels": uses_labels,
            "uses_validation_labels": False,
            "uses_test_labels": False,
            "k": int(mask.sum()),
            "score_min": float(np.min(scores)),
            "score_max": float(np.max(scores)),
            "score_mean_selected": float(scores[mask].mean()),
        }
        # Persist top scores for charts / audit
        top_idx = np.argsort(scores)[::-1][:50]
        for rank, idx in enumerate(top_idx, start=1):
            score_tables.append(
                {
                    "method": method,
                    "rank": rank,
                    "feature_index": int(idx),
                    "feature_name": names[idx],
                    "score": float(scores[idx]),
                    "selected_in_top_k": bool(mask[idx]),
                }
            )
        _plot_importance(
            names,
            scores,
            mask,
            title=f"Top features — {METHOD_LABELS[method].replace(chr(10), ' ')}",
            out_path=paths["figures"] / f"feature_importance_{method}.png",
        )
        joblib.dump(
            {"method": method, "scores": scores, "mask": mask, "k": k},
            paths["exp"] / f"selector_{method}.joblib",
        )

    pd.DataFrame(score_tables).to_csv(paths["metrics"] / "feature_selection_top_scores.csv", index=False)

    # Train / evaluate each model × method on validation only
    rows = []
    for method in METHOD_ORDER:
        Xtr = apply_mask(X_train_full, masks[method])
        Xva = apply_mask(X_val_full, masks[method])
        for model_name in MODEL_ORDER:
            print(f"Training {model_name} with {method} ({Xtr.shape[1]} feats)...", flush=True)
            pred = _train_predict(model_name, Xtr, y_train, Xva, random_state)
            metrics = evaluate_multiclass(y_val, pred, class_names)
            rows.append(
                {
                    "model": model_name,
                    "selection_method": method,
                    "supervised_selection": method != "no_supervised_fs",
                    "n_features": int(Xtr.shape[1]),
                    "n_train": int(Xtr.shape[0]),
                    "n_validation": int(Xva.shape[0]),
                    "accuracy": metrics["accuracy"],
                    "precision": metrics["precision"],
                    "recall": metrics["recall"],
                    "micro_f1": metrics["micro_f1"],
                    "macro_f1": metrics["macro_f1"],
                    "f1_weighted": metrics["f1_weighted"],
                }
            )

    results = pd.DataFrame(rows)
    results_path = paths["metrics"] / "feature_selection_comparison.csv"
    results.to_csv(results_path, index=False)

    # F1 / metric deltas vs no supervised FS
    base = results[results["selection_method"] == "no_supervised_fs"].set_index("model")
    delta_rows = []
    for method in METHOD_ORDER:
        if method == "no_supervised_fs":
            continue
        sub = results[results["selection_method"] == method].set_index("model")
        for model in MODEL_ORDER:
            delta_rows.append(
                {
                    "model": model,
                    "selection_method": method,
                    "delta_accuracy": float(sub.loc[model, "accuracy"] - base.loc[model, "accuracy"]),
                    "delta_precision": float(sub.loc[model, "precision"] - base.loc[model, "precision"]),
                    "delta_recall": float(sub.loc[model, "recall"] - base.loc[model, "recall"]),
                    "delta_micro_f1": float(sub.loc[model, "micro_f1"] - base.loc[model, "micro_f1"]),
                    "delta_macro_f1": float(sub.loc[model, "macro_f1"] - base.loc[model, "macro_f1"]),
                }
            )
    deltas = pd.DataFrame(delta_rows)
    deltas_path = paths["metrics"] / "feature_selection_f1_deltas.csv"
    deltas.to_csv(deltas_path, index=False)

    # Best supervised method per model (by validation micro_f1)
    best_rows = []
    for model in MODEL_ORDER:
        sub = results[(results["model"] == model) & (results["supervised_selection"])]
        best = sub.sort_values("micro_f1", ascending=False).iloc[0]
        best_rows.append(
            {
                "model": model,
                "best_selection_method": best["selection_method"],
                "delta_accuracy": float(best["accuracy"] - base.loc[model, "accuracy"]),
                "delta_micro_f1": float(best["micro_f1"] - base.loc[model, "micro_f1"]),
                "delta_macro_f1": float(best["macro_f1"] - base.loc[model, "macro_f1"]),
            }
        )
    best_delta = pd.DataFrame(best_rows)
    _plot_f1_heatmap(best_delta, paths["figures"] / "feature_selection_f1_deltas.png")
    _plot_grouped_comparison(results, paths["figures"] / "feature_selection_comparison.png")

    # Research interpretation
    overall_best = results.sort_values("micro_f1", ascending=False).iloc[0]
    mi_mean_delta = float(deltas.loc[deltas["selection_method"] == "mutual_information", "delta_micro_f1"].mean())
    rf_mean_delta = float(deltas.loc[deltas["selection_method"] == "rf_importance", "delta_micro_f1"].mean())
    pcc_mean_delta = float(deltas.loc[deltas["selection_method"] == "pcc_inspired_gong", "delta_micro_f1"].mean())
    any_help = any(best_delta["delta_micro_f1"] > 0.005)

    interpretation = f"""# Feature selection experiment — TCM-SD (validation)

## Question

Does selecting informative symptom-derived features improve multiclass TCM syndrome classification for Random Forest, Logistic Regression, and SVM?

## Data & leakage controls

- Same leakage-aware **train / validation** rows as the traditional-ML baselines.
- Feature pool: train-fitted char TF-IDF + length features + length bins (**no** re-fit on validation/test).
- All selectors scored on **training labels only**. Validation/test labels never entered selection.
- Test partition unused for selection and unused for ranking methods.
- Dimensionality matched at **k={k}** features for every arm.

## Methods

| Method | Supervision | Notes |
|--------|-------------|-------|
| `no_supervised_fs` | None | Variance ranking on train **X only**, top-k truncate |
| `mutual_information` | Train labels | Discrete MI on **binarized** n-gram presence (train subsample; continuous dense MI was intractable at this scale) |
| `rf_importance` | Train labels | ExtraTrees importances on a train subsample over the same candidates |
| `pcc_inspired_gong` | Train labels | **Parent-paper adaptation** (see below) |

Unsupervised variance prefilter to 6,000 candidates (train **X** only) is used before MI / importance / PCC scoring for tractability. The `no_supervised_fs` arm ranks the full pool by variance and keeps top-k.

### Parent-paper adaptation (accurate claim)

**Gong et al. 2023 (PCC-MLRF)** combines multi-label ReliefF with Pearson-correlation neighbor weights, then keeps top-weighted symptoms for MLDF. We **do not** reimplement full ML-ReliefF / PCC-MLRF: TCM-SD is **multiclass** (one `norm_syndrome`), and ReliefF over ~38k×20k is not feasible in this experiment. Instead we use a **PCC-inspired supervised filter**: mean \\(|\\rho|\\) between each feature and one-hot syndrome indicators on a training subsample, then keep top-k. This preserves Gong’s Pearson-correlation ranking idea as a filter, not the deep-forest stack.

**Huang et al. 2022** relies on four-exam field structure + learned cross features (not Relief/MI filters). **Chen et al. 2024** uses embeddings rather than classic selection. Those are documented as out-of-scope for this traditional-ML ablation (no deep learning in this round).

## Validation comparison

See `results/metrics/feature_selection_comparison.csv` and `results/figures/feature_selection_comparison.png`.

F1 / accuracy deltas vs no supervised FS: `results/metrics/feature_selection_f1_deltas.csv`, `results/figures/feature_selection_f1_deltas.png`.

Feature importance charts: `results/figures/feature_importance_*.png`.

## Headline numbers

- Best validation cell: **{MODEL_LABELS[overall_best['model']]}** + **{overall_best['selection_method']}** (micro-F1={overall_best['micro_f1']:.4f}, accuracy={overall_best['accuracy']:.4f}, macro-F1={overall_best['macro_f1']:.4f}).
- Mean Δ micro-F1 vs no supervised FS: MI={mi_mean_delta:+.4f}, RF-importance={rf_mean_delta:+.4f}, PCC-inspired={pcc_mean_delta:+.4f}.

## Interpretation — does selecting informative symptoms help?

{"Yes — at least one supervised selector improved micro-F1 by >0.5 pp for one or more classifiers relative to variance truncation at the same k." if any_help else "Not clearly — supervised selectors did not meaningfully beat unsupervised variance truncation at the same k on average. The TF-IDF pool is already sparse and informative; further label-guided pruning yields limited gains (or small regressions) for these linear/tree baselines."}

In this multiclass TCM-SD setting, feature selection is best read as **controlled sparsification for interpretability and possible small gains**, not a guaranteed accuracy booster. Mutual information and model-based importance remain useful for **highlighting which n-gram / length features track syndromes**, aligning with the parent papers’ emphasis on symptom relevance even when the exact ReliefF/cross-network machinery is adapted or deferred.

## Artifacts

- Selectors: `artifacts/feature_selection/selector_*.joblib`
- Tables: `results/metrics/feature_selection_*.csv`
- Figures: `results/figures/feature_selection_*.png`, `results/figures/feature_importance_*.png`
"""

    interp_path = paths["docs"] / "feature_selection_experiment.md"
    interp_path.write_text(interpretation, encoding="utf-8")
    (paths["metrics"] / "feature_selection_interpretation.md").write_text(interpretation, encoding="utf-8")

    summary = {
        "k": k,
        "pool_n_features": int(X_train_full.shape[1]),
        "selection_meta": selection_meta,
        "results_csv": str(results_path),
        "deltas_csv": str(deltas_path),
        "interpretation": str(interp_path),
        "best_row": overall_best.to_dict(),
        "mean_delta_micro_f1": {
            "mutual_information": mi_mean_delta,
            "rf_importance": rf_mean_delta,
            "pcc_inspired_gong": pcc_mean_delta,
        },
        "holdout_policy": {
            "validation_labels_in_selection": False,
            "test_labels_in_selection": False,
            "test_used_for_ranking": False,
        },
    }
    (paths["exp"] / "experiment_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary
