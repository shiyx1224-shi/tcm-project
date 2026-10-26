# Traditional ML comparison (validation)

Fair comparison on the **same** frozen TCM-SD train / validation matrices and preprocessor. Split fractions were not changed. **The held-out test set was not used to pick the best model.** No deep learning in this round.

## Validation metrics

Source of truth: [`results/metrics/model_comparison.csv`](../results/metrics/model_comparison.csv) · chart: [`results/figures/model_comparison.png`](../results/figures/model_comparison.png)

| Model | Accuracy | Precision | Recall | Micro-F1 | Macro-F1 |
|-------|---------:|----------:|-------:|---------:|---------:|
| **SVM (LinearSVC)** | **0.7517** | **0.8187** | **0.7517** | **0.7517** | **0.4745** |
| Random Forest | 0.7314 | 0.7833 | 0.7314 | 0.7314 | 0.4312 |
| Logistic Regression | 0.5120 | 0.7763 | 0.5120 | 0.5120 | 0.3316 |

## Which performs best?

**SVM (LinearSVC) is the best traditional ML algorithm so far** on validation accuracy, precision, recall, micro-F1, and macro-F1. Random Forest is a close second (~2 pp accuracy behind). Logistic Regression lags mainly on recall / F1 in this 148-class long-tailed setting.

## Why the ranking makes sense

- **SVM** maximizes margin separation in the shared 5,000-D TF-IDF space; with class balancing it recovers more rare syndromes (highest macro-F1) while staying linear and compact.
- **Random Forest** captures non-linear interactions but, at the chosen depth / leaf settings, does not quite match the linear margin classifier on this sparse text representation.
- **Logistic Regression** is the lightest linear baseline; similar weighted precision to the others but weaker recall, so accuracy and F1 drop.

Test remains sealed for a future final evaluation after model selection is locked on validation.
