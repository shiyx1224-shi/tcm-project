# Processed TCM-SD matrices

Regenerate with:

```bash
bash scripts/download_tcm_sd.sh
python scripts/run_preprocess.py
python scripts/check_splits.py
```

Large matrices (`X_*.npz`, row parquets, `y_*.joblib`) are produced locally and are gitignored. Fitted preprocessor metadata lives in `artifacts/preprocess/`.
