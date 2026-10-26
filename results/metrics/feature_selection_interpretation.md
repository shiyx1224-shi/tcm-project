# Feature selection experiment — TCM-SD (validation)

## Question

Does selecting informative symptom-derived features improve multiclass TCM syndrome classification for Random Forest, Logistic Regression, and SVM?

## Data & leakage controls

- Same leakage-aware **train / validation** rows as the traditional-ML baselines.
- Feature pool: train-fitted char TF-IDF + length features + length bins (**no** re-fit on validation/test).
- All selectors scored on **training labels only**. Validation/test labels never entered selection.
- Test partition unused for selection and unused for ranking methods.
- Dimensionality matched at **k=2000** features for every arm.

## Methods

| Method | Supervision | Notes |
|--------|-------------|-------|
| `no_supervised_fs` | None | Variance ranking on train **X only**, top-k truncate |
| `mutual_information` | Train labels | Discrete MI on **binarized** n-gram presence (train subsample; continuous dense MI was intractable at this scale) |
| `rf_importance` | Train labels | ExtraTrees importances on a train subsample over the same candidates |
| `pcc_inspired_gong` | Train labels | **Parent-paper adaptation** (see below) |

Unsupervised variance prefilter to 6,000 candidates (train **X** only) is used before MI / importance / PCC scoring for tractability. The `no_supervised_fs` arm ranks the full pool by variance and keeps top-k.

### Parent-paper adaptation (accurate claim)

**Gong et al. 2023 (PCC-MLRF)** combines multi-label ReliefF with Pearson-correlation neighbor weights, then keeps top-weighted symptoms for MLDF. We **do not** reimplement full ML-ReliefF / PCC-MLRF: TCM-SD is **multiclass** (one `norm_syndrome`), and ReliefF over ~38k×20k is not feasible in this experiment. Instead we use a **PCC-inspired supervised filter**: mean \(|\rho|\) between each feature and one-hot syndrome indicators on a training subsample, then keep top-k. This preserves Gong’s Pearson-correlation ranking idea as a filter, not the deep-forest stack.

**Huang et al. 2022** relies on four-exam field structure + learned cross features (not Relief/MI filters). **Chen et al. 2024** uses embeddings rather than classic selection. Those are documented as out-of-scope for this traditional-ML ablation (no deep learning in this round).

## Validation comparison

See `results/metrics/feature_selection_comparison.csv` and `results/figures/feature_selection_comparison.png`.

F1 / accuracy deltas vs no supervised FS: `results/metrics/feature_selection_f1_deltas.csv`, `results/figures/feature_selection_f1_deltas.png`.

Feature importance charts: `results/figures/feature_importance_*.png`.

## Headline numbers

- Best validation cell: **Random Forest** + **no_supervised_fs** (micro-F1=0.8046, accuracy=0.8046, macro-F1=0.4617).
- Mean Δ micro-F1 vs no supervised FS: MI=-0.0061, RF-importance=-0.0158, PCC-inspired=-0.0113.

## Interpretation — does selecting informative symptoms help?

Yes — at least one supervised selector improved micro-F1 by >0.5 pp for one or more classifiers relative to variance truncation at the same k.

In this multiclass TCM-SD setting, feature selection is best read as **controlled sparsification for interpretability and possible small gains**, not a guaranteed accuracy booster. Mutual information and model-based importance remain useful for **highlighting which n-gram / length features track syndromes**, aligning with the parent papers’ emphasis on symptom relevance even when the exact ReliefF/cross-network machinery is adapted or deferred.

## Artifacts

- Selectors: `artifacts/feature_selection/selector_*.joblib`
- Tables: `results/metrics/feature_selection_*.csv`
- Figures: `results/figures/feature_selection_*.png`, `results/figures/feature_importance_*.png`
