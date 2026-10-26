# Random Forest vs Logistic Regression (validation)

Fair comparison on the **same** frozen TCM-SD train / validation matrices and the **same** train-fitted preprocessor. Split fractions and group IDs were not changed. Test remains untouched. SVM is not implemented yet.

## Task type

Multiclass (one `norm_syndrome` per row). Multi-label wrappers are not used.

## Validation metrics

Source of truth: [`results/metrics/model_comparison.csv`](../results/metrics/model_comparison.csv)

| Model | Accuracy | Precision | Recall | Micro-F1 | Macro-F1 |
|-------|---------:|----------:|-------:|---------:|---------:|
| Random Forest | **0.7314** | **0.7833** | **0.7314** | **0.7314** | **0.4312** |
| Logistic Regression | 0.5120 | 0.7763 | 0.5120 | 0.5120 | 0.3316 |

Precision / recall above are the weighted aliases stored for reporting; CSV also includes macro averages.

## What differs between the models

| | Random Forest | Logistic Regression |
|--|---------------|---------------------|
| Decision surface | Non-linear (ensemble of trees) | Linear (multinomial logit) |
| Class balance | `balanced_subsample` | `balanced` |
| Fit representation | Dense float32 | Dense float32 (`lbfgs`) |
| Artifact size | ~380 MB | ~3–4 MB |
| Strength | Interactions among symptoms / n-grams | Calibrated linear odds; compact |

## Which is better?

**Random Forest performs better on the validation set** across accuracy (+0.22), recall, micro-F1, and macro-F1. Weighted precision is nearly tied, so the main gap is recall on this long-tailed 148-class label space: the tree ensemble recovers more true syndromes, including rarer ones (higher macro-F1).

Logistic Regression remains a useful linear baseline and a much lighter inference artifact, but it is not the stronger model under the current shared feature pipeline.
