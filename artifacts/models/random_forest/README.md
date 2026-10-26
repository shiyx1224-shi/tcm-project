# Random Forest artifacts

Large `*.joblib` binaries are gitignored. Regenerate with:

```bash
python scripts/run_preprocess.py   # if needed
python scripts/train_random_forest.py
```

Tracked here: validation metrics, summary, and a small prediction preview CSV.

Inference:

```bash
python scripts/predict_syndrome.py --artifacts artifacts/models/random_forest \
  --chief-complaint "..." --description "..." --detection "..."
```
