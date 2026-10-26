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
| `rf_importance` | Train labels | ExtraTrees importances on a train subsample over variance-prefiltered candidates |
| `pcc_inspired_gong` | Train labels | **Parent-paper adaptation** (see below) |

Unsupervised variance prefilter to 6,000 candidates (train **X** only) is used before MI / importance / PCC scoring for tractability. The `no_supervised_fs` arm ranks the full pool by variance and keeps top-k.

### Parent-paper adaptation (accurate claim)

**Gong et al. 2023 (PCC-MLRF)** combines multi-label ReliefF with Pearson-correlation neighbor weights, then keeps top-weighted symptoms for MLDF. We **do not** reimplement full ML-ReliefF / PCC-MLRF: TCM-SD is **multiclass** (one `norm_syndrome`), and ReliefF over ~38k×20k is not feasible in this experiment. Instead we use a **PCC-inspired supervised filter**: mean \(|\rho|\) between each feature and one-hot syndrome indicators on a training subsample, then keep top-k. This preserves Gong’s Pearson-correlation ranking idea as a filter, not the deep-forest stack.

**Huang et al. 2022** relies on four-exam field structure + learned cross features (not Relief/MI filters). **Chen et al. 2024** uses embeddings rather than classic selection. Those are documented as out-of-scope for this traditional-ML ablation (no deep learning in this round).

## Validation comparison table

Source: [`results/metrics/feature_selection_comparison.csv`](../results/metrics/feature_selection_comparison.csv) · chart: [`results/figures/feature_selection_comparison.png`](../results/figures/feature_selection_comparison.png)

| Model | Selection | Accuracy | Precision | Recall | Micro-F1 | Macro-F1 |
|-------|-----------|---------:|----------:|-------:|---------:|---------:|
| Random Forest | no supervised FS | **0.8046** | 0.8026 | **0.8046** | **0.8046** | 0.4617 |
| Random Forest | mutual information | 0.8015 | 0.8039 | 0.8015 | 0.8015 | 0.4454 |
| Random Forest | RF importance | 0.7590 | 0.7835 | 0.7590 | 0.7590 | 0.4236 |
| Random Forest | PCC-inspired (Gong) | 0.7899 | 0.7961 | 0.7899 | 0.7899 | 0.4430 |
| Logistic Regression | no supervised FS | 0.4699 | 0.7588 | 0.4699 | 0.4699 | 0.2917 |
| Logistic Regression | mutual information | 0.4601 | 0.7731 | 0.4601 | 0.4601 | 0.2872 |
| Logistic Regression | RF importance | 0.4546 | 0.7700 | 0.4546 | 0.4546 | 0.3022 |
| Logistic Regression | PCC-inspired (Gong) | 0.4509 | 0.7550 | 0.4509 | 0.4509 | 0.3061 |
| SVM | no supervised FS | 0.7360 | 0.8074 | 0.7360 | 0.7360 | 0.4434 |
| SVM | mutual information | 0.7306 | 0.8117 | 0.7306 | 0.7306 | 0.4423 |
| SVM | RF importance | **0.7494** | **0.8127** | **0.7494** | **0.7494** | **0.4752** |
| SVM | PCC-inspired (Gong) | 0.7360 | 0.8099 | 0.7360 | 0.7360 | 0.4607 |

## F1-score differences vs no supervised FS

Source: [`results/metrics/feature_selection_f1_deltas.csv`](../results/metrics/feature_selection_f1_deltas.csv) · heatmap: [`results/figures/feature_selection_f1_deltas.png`](../results/figures/feature_selection_f1_deltas.png)

| Model | Method | Δ Micro-F1 | Δ Macro-F1 |
|-------|--------|-----------:|-----------:|
| Random Forest | MI | −0.0031 | −0.0163 |
| Random Forest | RF importance | −0.0456 | −0.0381 |
| Random Forest | PCC-inspired | −0.0148 | −0.0187 |
| Logistic Regression | MI | −0.0098 | −0.0044 |
| Logistic Regression | RF importance | −0.0153 | **+0.0105** |
| Logistic Regression | PCC-inspired | −0.0190 | **+0.0144** |
| SVM | MI | −0.0054 | −0.0011 |
| SVM | RF importance | **+0.0135** | **+0.0318** |
| SVM | PCC-inspired | 0.0000 | **+0.0173** |

Mean Δ micro-F1 across classifiers: MI −0.0061, RF-importance −0.0158, PCC-inspired −0.0113.

## Feature importance charts

- [`results/figures/feature_importance_no_supervised_fs.png`](../results/figures/feature_importance_no_supervised_fs.png)
- [`results/figures/feature_importance_mutual_information.png`](../results/figures/feature_importance_mutual_information.png)
- [`results/figures/feature_importance_rf_importance.png`](../results/figures/feature_importance_rf_importance.png)
- [`results/figures/feature_importance_pcc_inspired_gong.png`](../results/figures/feature_importance_pcc_inspired_gong.png)

Top-score audit CSV: `results/metrics/feature_selection_top_scores.csv`.

## Research interpretation — does selecting informative symptoms help?

**Mixed, classifier-dependent — not a blanket win.**

1. **Random Forest** already works well on high-variance TF-IDF dimensions. Supervised filters (especially tree importance re-selection) **hurt** RF micro/macro F1 at matched k=2000. The most informative “symptoms” for RF appear to be the high-variance n-grams themselves; further label-guided pruning discards useful interactions.
2. **Logistic Regression** loses overall accuracy/micro-F1 under supervised selection, but **macro-F1 rises** with RF-importance and PCC-inspired filters — rare syndromes benefit even when frequent-class accuracy dips.
3. **SVM** is the clearest beneficiary: **RF-importance selection improves micro-F1 (+1.3 pp) and macro-F1 (+3.2 pp)** vs variance truncation. PCC-inspired selection leaves micro-F1 flat but improves macro-F1 (+1.7 pp).

**Bottom line:** Selecting informative symptoms *can* help — especially margin-based SVM and rare-class (macro) performance — but it is **not universally better** than unsupervised variance truncation for tree ensembles on this sparse clinical TF-IDF pool. Feature ranking remains valuable for **interpretability** (which n-grams track syndromes), consistent with Gong’s emphasis on symptom weighting, even though full PCC-MLRF / Huang cross-networks / Chen embeddings were not reproduced here.

No deep learning was used in this experiment. Test labels were never used for selection or model ranking.
