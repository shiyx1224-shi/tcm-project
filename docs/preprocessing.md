# Split & preprocessing pipeline (DS 340W)

**No classifier is trained here.** This stage only creates partitions and transforms features.

## Split

| Partition | Target share | Role |
|-----------|-------------:|------|
| train | 70% | Fit vectorizers, scalers, encoders, feature selection |
| validation | 10% | Future model selection only |
| test | 20% | **Final evaluation only — do not fit on this** |

- `random_state=42`
- Groups connect rows that share the same `user_id` **or** the same clinical text fingerprint (`chief_complaint + description + detection`) so patients / duplicate cases do not cross splits

## Features & target

| Role | Columns |
|------|---------|
| Text features | `chief_complaint`, `description`, `detection` → character TF-IDF |
| Numerical | engineered lengths / token approximations → `StandardScaler` |
| Categorical | description length bins → `OneHotEncoder(handle_unknown="ignore")` |
| Target | `norm_syndrome` → `LabelEncoder` (fit on train) |
| Excluded (leakage / IDs) | `user_id`, `syndrome`, `norm_syndrome` (as input), `lcd_id`, `lcd_name` |

Feature selection: `SelectKBest(chi2)` fit on training data only.

## Commands

```bash
pip install -r requirements.txt
# ensure raw JSON exists
bash scripts/download_tcm_sd.sh
python scripts/run_preprocess.py
python scripts/check_splits.py
```

## Outputs

- `data/processed/{train,validation,test}_rows.parquet` — audited row partitions
- `data/processed/X_{split}.npz` — sparse feature matrices
- `data/processed/y_{split}.joblib` — encoded labels (+ unknown = -1 if needed)
- `artifacts/preprocess/syndrome_preprocessor.joblib` — fitted pipeline
- `artifacts/preprocess/split_preprocess_report.json` — sizes + check results
