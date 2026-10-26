# SVM model (multiclass LinearSVC)

Third traditional ML baseline on TCM-SD. Uses the **same** frozen train/validation matrices and preprocessor as Random Forest and Logistic Regression. Test remains held out and is **not** used for model selection.

## Task type

Single-label multiclass → no multi-label wrapper. Implementation: `sklearn.svm.LinearSVC` (OvR). Kernel `SVC` is intentionally skipped for this baseline because full kernel SVM on ~38k × 5k × 148 classes is not practical here.

## Defaults

| Item | Choice |
|------|--------|
| Estimator | `LinearSVC` |
| `C` | 1.0 |
| `class_weight` | `balanced` |
| `dual` | `auto` |
| `max_iter` | 5000 |

## Commands

```bash
python scripts/train_svm.py
python scripts/predict_syndrome_svm.py \
  --chief-complaint "头痛，头晕" \
  --description "患者头痛头晕三日，伴恶心。" \
  --detection "舌淡红，苔薄白，脉弦。"
python scripts/compare_models.py
```

Artifacts: `artifacts/models/svm/`  
Comparison: `results/metrics/model_comparison.csv`, `results/figures/model_comparison.png`
