# Si Zhen Desk · DS340W

Teaching workbench for traditional Chinese medicine (TCM) **syndrome differentiation** (辨证). You chart signs from the four examinations (四诊); the desk returns every pattern that fits instead of forcing one class.

Educational instrument only. It does **not** diagnose, prescribe, or replace a licensed clinician.

**GitHub home:** [github.com/shiyx1224-shi/tcm-project](https://github.com/shiyx1224-shi/tcm-project)

## Public research dataset (required link)

**Dataset:** TCM-SD (54,152 real clinical records → 148 syndrome labels)  
**Public link:** https://github.com/Borororo/ZY-BERT  
**License:** CC BY-NC-SA 4.0 (dataset; non-commercial research with attribution)  
**Paper:** Ren et al., CCL 2022 — https://aclanthology.org/2022.ccl-1.80/  
**Local copy / schema / download steps:** [`DATASET.md`](DATASET.md) · files under `data/raw/TCM-SD/`  
**Re-download:** `bash scripts/download_tcm_sd.sh`  
**EDA notebook (no training):** [`notebooks/01_data_exploration.ipynb`](notebooks/01_data_exploration.ipynb)  
**Split + preprocess:** [`docs/preprocessing.md`](docs/preprocessing.md) · `python scripts/run_preprocess.py`  
**Random Forest baseline (multiclass):** [`docs/random_forest.md`](docs/random_forest.md) · `python scripts/train_random_forest.py` · `python scripts/predict_syndrome.py`  
**Logistic Regression (same split/features):** [`docs/logistic_regression.md`](docs/logistic_regression.md) · `python scripts/train_logistic_regression.py`  
**SVM / LinearSVC (same split/features):** [`docs/svm.md`](docs/svm.md) · `python scripts/train_svm.py`  
**Model comparison:** [`docs/model_comparison.md`](docs/model_comparison.md) · `results/metrics/model_comparison.csv` · `results/figures/model_comparison.png` · `python scripts/compare_models.py`  
**Feature selection experiment:** [`docs/feature_selection_experiment.md`](docs/feature_selection_experiment.md) · `python scripts/run_feature_selection_experiment.py`  
**Huang-inspired CNN (adapted Cross-FGCNN):** [`docs/huang_cnn.md`](docs/huang_cnn.md) · `python scripts/train_huang_cnn.py`

## Parent papers

| # | Paper | What this desk takes |
|---|-------|----------------------|
| 1 | Gong, Jiang, Chen, and Qi. *A syndrome differentiation model of TCM based on multi-label deep forest using biomedical text mining.* Frontiers in Genetics, 2023. [doi:10.3389/fgene.2023.1272016](https://doi.org/10.3389/fgene.2023.1272016) | Multi-label syndromes; synonym-normalized symptoms; set metrics (Hamming, one-error, AP) on small charts |
| 2 | Huang, Miao, Chen, Zhong, Yang, Ma, and Wen. *A traditional Chinese medicine syndrome classification model based on cross-feature generation by convolution neural network.* JMIR Medical Informatics, 2022. [doi:10.2196/29290](https://doi.org/10.2196/29290) | Four-examination structure; sparse tongue/pulse; named cross features; dysmenorrhea pattern family |
| 3 | Chen, Zhang, Liu, Wang, Jin, Yang, and Zhang. *Traditional Chinese medicine diagnostic prediction model for holistic syndrome differentiation based on deep learning.* Integrative Medicine Research, 2024. [doi:10.1016/j.imr.2023.101019](https://doi.org/10.1016/j.imr.2023.101019) | Holistic principles/organs/pathology; competing pairs (exterior–interior, cold–heat, deficiency–excess); symptom co-occurrence view |

The live score is a **weighted pattern profile**, not a retrained deep forest, CNN, or BERT model. Hospital and guideline corpora from the papers are not in this repository; published accuracies are not claimed here.

## App surfaces

- **Chart** — select symptoms by examination, or parse a free-text description into the dictionary
- **Sample charts** — original teaching narratives (kidney, stomach, dysmenorrhea, holistic)
- **Pattern atlas** — which key signs travel together
- **Teaching lab** — multi-label metrics vs overlap / ML-kNN baselines on the teaching set
- **Parent papers** — how each study maps onto the desk

## Lenses

- **Holistic** — eight principles, organ location, and pathology
- **Kidney disease** — spleen-kidney yang/yin deficiency, liver-kidney yin deficiency, damp turbidity (may co-exist)
- **Stomach disease** — deficiency cold, liver-stomach disharmony, stomach yin deficiency, damp-heat, food stagnation
- **Dysmenorrhea** — nine period-pain patterns, including mixed cold, stasis, deficiency, and damp-heat

## Run locally

```bash
npm install
npm run dev
```

Open [http://127.0.0.1:4317](http://127.0.0.1:4317).

```bash
npm run check   # sample-chart rank checks + teaching-set metrics
npm run lint
npm run build
```

## ML baselines (TCM-SD)

TCM-SD is **single-label multiclass** (one `norm_syndrome` per row). Models share the same leakage-aware 70/10/20 partitions and are scored on validation. **Test is not used for model selection.**

```bash
pip install -r requirements-ml.txt
python scripts/run_preprocess.py          # if data/processed is empty
python scripts/train_random_forest.py
python scripts/train_logistic_regression.py
python scripts/train_svm.py
python scripts/train_huang_cnn.py         # Huang 2022–inspired CNN (adaptation, not exact reproduction)
python scripts/compare_models.py
```

Artifacts: `artifacts/models/{random_forest,logistic_regression,svm,huang_cnn}/`.  
Comparison: `results/metrics/model_comparison.csv`, `results/figures/model_comparison.png`.

Feature-selection ablation: `python scripts/run_feature_selection_experiment.py`.

## Course note (DS340W)

This is a reproduction-style project: we implement the *ideas* from the three parent papers (multi-label reading, sparse four examinations with crosses, holistic constraints) as an interactive teaching instrument with transparent scoring, not a black-box retrain of their neural models on proprietary clinical data. The Random Forest path above is the first supervised baseline on the public TCM-SD release.

**Research foundation (verified citations, parent-paper methods):** [`docs/parent_papers.md`](docs/parent_papers.md)  
**Selected public dataset (link, license, features):** [`DATASET.md`](DATASET.md)
