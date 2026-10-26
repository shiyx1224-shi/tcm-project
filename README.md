# TCM Syndrome Desk · DS340W TCM Syndrome Classification

Teaching workbench and machine-learning study for traditional Chinese medicine (TCM) **syndrome differentiation** (辨证).

Educational / research instrument only. It does **not** diagnose, prescribe, or replace a licensed clinician.

**GitHub:** [github.com/shiyx1224-shi/tcm-project](https://github.com/shiyx1224-shi/tcm-project)

---

## Research question

> How accurately can machine learning models classify TCM syndromes based on patients’ symptoms and clinical data?

This repo answers that question on the **public TCM-SD** benchmark with a leakage-aware 70/10/20 split, traditional ML baselines, feature-selection ablations, parent-paper–inspired deep models (adaptations, not exact reproductions), and a locked held-out **test** evaluation of the validation winner.

---

## Three verified parent papers

| # | Citation | Method borrowed |
|---|----------|-----------------|
| 1 | Gong, Jiang, Chen, and Qi. *A syndrome differentiation model of TCM based on multi-label deep forest using biomedical text mining.* Frontiers in Genetics, 2023. [doi:10.3389/fgene.2023.1272016](https://doi.org/10.3389/fgene.2023.1272016) | Multi-label framing; Pearson-inspired symptom ranking (PCC-MLRF **adapted**; full MLDF not used — TCM-SD is multiclass) |
| 2 | Huang, Miao, Chen, Zhong, Yang, Ma, and Wen. *A traditional Chinese medicine syndrome classification model based on cross-feature generation by convolution neural network.* JMIR Medical Informatics, 2022. [doi:10.2196/29290](https://doi.org/10.2196/29290) | Cross network + FGCNN-style CNN (**AdaptedCrossFGCNN**; not Huang’s 60-field dysmenorrhea data) |
| 3 | Chen, Zhang, Liu, Wang, Jin, Yang, and Zhang. *Traditional Chinese medicine diagnostic prediction model for holistic syndrome differentiation based on deep learning.* Integrative Medicine Research, 2024. [doi:10.1016/j.imr.2023.101019](https://doi.org/10.1016/j.imr.2023.101019) | BERT + TextCNN over clinical text (**adapted** frozen Chinese BERT-family encoder; not Chen’s 21-label constraint head) |

Full methodology notes: [`docs/parent_papers.md`](docs/parent_papers.md).

---

## Public dataset link

| Item | Value |
|------|-------|
| **Dataset** | TCM-SD (54,152 clinical records → 148 `norm_syndrome` labels) |
| **Public link** | **https://github.com/Borororo/ZY-BERT** |
| **License** | CC BY-NC-SA 4.0 (dataset; non-commercial research with attribution) |
| **Paper** | Ren et al., CCL 2022 — https://aclanthology.org/2022.ccl-1.80/ |
| **Local path** | `data/raw/TCM-SD/` |
| **Details** | [`DATASET.md`](DATASET.md) |

```bash
bash scripts/download_tcm_sd.sh
```

---

## Methods (ML track)

1. **Leakage-aware split** — 70% train / 10% validation / 20% test by patient + clinical-text fingerprint groups (`random_state=42`).
2. **Train-only preprocessing** — char TF-IDF + length features + bins; `SelectKBest(chi2, k=5000)` fit on train only.
3. **Traditional ML** — Random Forest, Logistic Regression, Linear SVM on the same matrices.
4. **Feature selection ablation** — variance truncate vs mutual information / ExtraTrees importance / Gong-inspired Pearson filter (train labels only).
5. **Deep adaptations** — Huang-inspired Cross-FGCNN; Chen-inspired BERT+TextCNN.
6. **Final protocol** — choose best model by **validation micro-F1**, then score **test once**.

---

## Experimental results (measured)

Validation leaderboard (`results/metrics/model_comparison.csv`):

| Model | Accuracy | Micro-F1 | Macro-F1 |
|-------|---------:|---------:|---------:|
| **SVM (LinearSVC)** | **0.7517** | **0.7517** | **0.4745** |
| Random Forest | 0.7314 | 0.7314 | 0.4312 |
| Logistic Regression | 0.5120 | 0.5120 | 0.3316 |
| Chen-inspired BERT+CNN | 0.5007 | 0.5007 | 0.2521 |
| Huang-inspired CNN | 0.4635 | 0.4635 | 0.2112 |

**Selected model (validation only): SVM.** Held-out test (n=10,777):

| Split | Accuracy | Precision | Recall | Micro-F1 | Macro-F1 |
|-------|---------:|----------:|-------:|---------:|---------:|
| Validation | 0.7517 | 0.8187 | 0.7517 | 0.7517 | 0.4745 |
| **Test** | **0.7548** | **0.8137** | **0.7548** | **0.7548** | **0.4992** |

Feature selection did **not** uniformly improve micro-F1; adapted deep models did **not** beat TF-IDF SVM/RF on this setup. Full discussion: [`docs/final_evaluation.md`](docs/final_evaluation.md).

Figures: `results/figures/model_comparison.png`, `results/figures/final_*.png`.

---

## Install and run (ML)

```bash
python -m pip install -r requirements.txt
bash scripts/download_tcm_sd.sh
python scripts/run_preprocess.py
python scripts/check_splits.py
python scripts/train_random_forest.py
python scripts/train_logistic_regression.py
python scripts/train_svm.py
python scripts/compare_models.py
python scripts/run_feature_selection_experiment.py   # optional ablation
python scripts/train_huang_cnn.py                    # optional deep adaptation
python scripts/train_chen_bert_cnn.py                # optional deep adaptation
python scripts/run_final_evaluation.py               # validation winner → test once
python scripts/smoke_test_ml.py                      # link/load/leakage/results smoke check
```

`requirements-ml.txt` redirects to `requirements.txt` for older commands.

Predict with the selected SVM pipeline (after `train_svm.py`):

```bash
python scripts/predict_syndrome_svm.py \
  --chief-complaint "头痛，头晕" \
  --description "患者头痛头晕三日，伴恶心。" \
  --detection "舌淡红，苔薄白，脉弦。"
```

---

## Teaching UI (TCM Syndrome Desk)

Interactive four-examination desk for syndrome differentiation teaching (not the TCM-SD ML classifier):

```bash
npm install
npm run dev
```

Open [http://127.0.0.1:4317](http://127.0.0.1:4317).

```bash
npm run check
npm run lint
npm run build
```

Surfaces: Chart, Sample charts, Pattern atlas, Teaching lab, Parent papers. Lenses: Holistic / Kidney / Stomach / Dysmenorrhea.

---

## Repository hygiene

- **Not committed:** `/uploads` (local parent PDFs), extracted `train.json`/`dev.json`, large `*.npz` / row parquets / model `*.joblib`/`*.pt`, caches, `.env*`, tokens.
- **Committed:** public sample/zip/test.json, metrics CSVs/JSON, figures, docs, training code.
- Do not add private clinical dumps or API tokens to git.

---

## Doc index

| Doc | Contents |
|-----|----------|
| [`DATASET.md`](DATASET.md) | Dataset choice, license, schema, download |
| [`docs/parent_papers.md`](docs/parent_papers.md) | Verified parent-paper methods |
| [`docs/preprocessing.md`](docs/preprocessing.md) | Split + preprocess |
| [`docs/final_evaluation.md`](docs/final_evaluation.md) | Selection, test, discussion |
| [`docs/huang_cnn.md`](docs/huang_cnn.md) / [`docs/chen_bert_cnn.md`](docs/chen_bert_cnn.md) | Deep adaptations |
