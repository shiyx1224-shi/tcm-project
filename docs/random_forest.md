# Initial Random Forest model (multiclass)

TCM-SD assigns **one** `norm_syndrome` per record (148 classes), so this baseline is **multiclass**, not multi-label. Exact-match accuracy and Hamming loss are recorded as not applicable.

## What is trained

| Item | Choice |
|------|--------|
| Model | `sklearn.ensemble.RandomForestClassifier` |
| Features | Prepared sparse matrices from `scripts/run_preprocess.py` (dense at fit time) |
| Fit on | `train` only |
| Evaluated on | `validation` only |
| Held out | `test` (untouched) |

Default hyperparameters: `n_estimators=100`, `max_depth=40`, `min_samples_leaf=2`, `class_weight=balanced_subsample`, `random_state=42`.

## Metrics (validation)

- Accuracy
- Precision / Recall (weighted aliases; macro & weighted also stored)
- Micro-F1
- Macro-F1

## Commands

```bash
pip install -r requirements.txt
python scripts/run_preprocess.py          # if matrices are missing
python scripts/train_random_forest.py
python scripts/predict_syndrome.py \
  --chief-complaint "头痛，头晕" \
  --description "患者头痛头晕三日，伴恶心。" \
  --detection "舌淡红，苔薄白，脉弦。"
```

## Artifacts

Under `artifacts/models/random_forest/`:

| File | Role |
|------|------|
| `random_forest_model.joblib` | Fitted classifier |
| `syndrome_rf_pipeline.joblib` | Preprocessor + model for inference |
| `validation_metrics.json` | Full validation metrics + classification report |
| `validation_summary.json` | Compact metrics without per-class report |
| `validation_preview.csv` | First 50 validation true/pred labels |
