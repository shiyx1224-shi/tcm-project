# Model comparison (validation)

Same frozen TCM-SD **train / validation** partitions. **Test unused for selection.**

| Model | Accuracy | Precision | Recall | Micro-F1 | Macro-F1 |
|-------|---------:|----------:|-------:|---------:|---------:|
| **SVM (LinearSVC)** | **0.7517** | **0.8187** | **0.7517** | **0.7517** | **0.4745** |
| Random Forest | 0.7314 | 0.7833 | 0.7314 | 0.7314 | 0.4312 |
| Logistic Regression | 0.5120 | 0.7763 | 0.5120 | 0.5120 | 0.3316 |
| Chen-inspired BERT+CNN | 0.5007 | 0.6411 | 0.5007 | 0.5007 | 0.2521 |
| Huang-inspired CNN | 0.4635 | 0.6125 | 0.4635 | 0.4635 | 0.2112 |

Source CSV: [`results/metrics/model_comparison.csv`](../results/metrics/model_comparison.csv) · chart: [`results/figures/model_comparison.png`](../results/figures/model_comparison.png)

**Best so far (validation):** SVM.

Deep models are **adaptations** of Huang 2022 and Chen 2024 — not exact reproductions. See [`docs/huang_cnn.md`](huang_cnn.md) and [`docs/chen_bert_cnn.md`](chen_bert_cnn.md). Gong et al. multi-label deep forest was **not** implemented: TCM-SD is single-label multiclass free text, not a multi-hot symptom matrix.
