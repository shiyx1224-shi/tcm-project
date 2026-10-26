# Model comparison (validation)

Same frozen TCM-SD **train / validation** partitions. **Test unused for selection.**

| Model | Accuracy | Precision | Recall | Micro-F1 | Macro-F1 |
|-------|---------:|----------:|-------:|---------:|---------:|
| **SVM (LinearSVC)** | **0.7517** | **0.8187** | **0.7517** | **0.7517** | **0.4745** |
| Random Forest | 0.7314 | 0.7833 | 0.7314 | 0.7314 | 0.4312 |
| Logistic Regression | 0.5120 | 0.7763 | 0.5120 | 0.5120 | 0.3316 |
| Huang-inspired CNN | 0.4635 | 0.6125 | 0.4635 | 0.4635 | 0.2112 |

Source CSV: [`results/metrics/model_comparison.csv`](../results/metrics/model_comparison.csv) · chart: [`results/figures/model_comparison.png`](../results/figures/model_comparison.png)

**Best so far (validation):** SVM. The Huang-inspired CNN is an **adaptation**, not an exact Cross-FGCNN reproduction; see [`docs/huang_cnn.md`](huang_cnn.md).
