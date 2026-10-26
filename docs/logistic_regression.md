# Logistic Regression model (multiclass)

Second supervised baseline on TCM-SD. Uses the **same** frozen train/validation matrices and preprocessor as the Random Forest baseline. No re-split. Test remains held out.

## Task type

TCM-SD has **one** `norm_syndrome` per row → **multiclass**. A multi-label wrapper (`MultiOutputClassifier`, `ClassifierChain`, etc.) is **not** applied.

## Model

| Item | Choice |
|------|--------|
| Estimator | `sklearn.linear_model.LogisticRegression` |
| Objective | multinomial multiclass (sklearn default; no multi-label wrapper) |
| Solver | `lbfgs` on dense float32 (same 5k features as RF) |
| Regularization | L2 via `C=1.0` |
| Class balance | `class_weight="balanced"` |
| Features | Same `X_train` / `X_validation` as Random Forest |

## Commands

```bash
python scripts/train_logistic_regression.py
python scripts/predict_syndrome_lr.py \
  --chief-complaint "头痛，头晕" \
  --description "患者头痛头晕三日，伴恶心。" \
  --detection "舌淡红，苔薄白，脉弦。"
python scripts/compare_models.py
```

## Artifacts

Under `artifacts/models/logistic_regression/`:

| File | Role |
|------|------|
| `logistic_regression_model.joblib` | Fitted classifier |
| `syndrome_lr_pipeline.joblib` | Preprocessor + model for inference |
| `validation_metrics.json` / `validation_summary.json` | Validation scores |
| `validation_preview.csv` | Spot-check predictions |

Comparison table: `results/metrics/model_comparison.csv`
