# Final evaluation — DS340W TCM syndrome classification

**Research question:** How accurately can machine learning models classify TCM syndromes based on patients’ symptoms and clinical data?

All numbers below are **measured** from artifacts under `results/` and `artifacts/models/`. Nothing is fabricated.

## 1. Integrity verification (pre-test)

- Split overlap checks: **PASS** (patient `user_id`, clinical `case_fingerprint`, and `leakage_group` intersections are all 0).
- Feature/label leakage checks: **PASS** (model text features = ['chief_complaint', 'description', 'detection']; banned ID/label columns absent).
- Preprocessor fit on train only; SelectKBest k=5000; 148 classes.
- Test matrix shape: [10777, 5000]; unknown labels in test encoding: 0.

Partition sizes:

| Partition | Rows | Patients | Fingerprints | Labels |
|-----------|-----:|---------:|-------------:|-------:|
| train | 37955 | 36646 | 33721 | 148 |
| validation | 5420 | 5225 | 4817 | 148 |
| test | 10777 | 10424 | 9637 | 148 |

## 2. Validation leaderboard (model selection)

Selection rule: maximize validation **micro_f1** on the shared baseline table `results/metrics/model_comparison.csv`. **Test was not consulted.**

| Rank | Model | Accuracy | Precision | Recall | Micro-F1 | Macro-F1 |
|-----:|-------|---------:|----------:|-------:|---------:|---------:|
| 1 | SVM (LinearSVC) | 0.7517 | 0.8187 | 0.7517 | 0.7517 | 0.4745 |
| 2 | Random Forest | 0.7314 | 0.7833 | 0.7314 | 0.7314 | 0.4312 |
| 3 | Logistic Regression | 0.5120 | 0.7763 | 0.5120 | 0.5120 | 0.3316 |
| 4 | Chen-inspired BERT+CNN | 0.5007 | 0.6411 | 0.5007 | 0.5007 | 0.2521 |
| 5 | Huang-inspired CNN | 0.4635 | 0.6125 | 0.4635 | 0.4635 | 0.2112 |

**Selected model: SVM (LinearSVC)** (validation micro_f1=0.7517).

## 3. Feature-selection experiment (measured)

Separate ablation at matched k=2000 (see `results/metrics/feature_selection_*.csv`). This did **not** change the primary baseline winner above (baselines use k=5000 chi2 features).

- Mean Δ micro-F1 vs unsupervised variance truncate: MI=-0.0061, RF-importance=-0.0158, PCC-inspired=-0.0113.
- SVM benefited from RF-importance selection (Δ micro-F1 +0.0135); Random Forest generally did not benefit from supervised filters at matched k.

## 4. Held-out test performance (selected SVM only)

Test n = 10777 (parquet rows 10777).

| Split | Accuracy | Precision | Recall | Micro-F1 | Macro-F1 |
|-------|---------:|----------:|-------:|---------:|---------:|
| Validation (selection) | 0.7517 | 0.8187 | 0.7517 | 0.7517 | 0.4745 |
| **Test (final)** | **0.7548** | **0.8137** | **0.7548** | **0.7548** | **0.4992** |

Figures: `results/figures/final_f1_comparison.png`, `results/figures/final_test_confusion_top15.png`, `results/figures/final_test_worst_classes.png`.

## 5. Error analysis (test)

Lowest-F1 syndromes (head of `results/metrics/final_test_per_class.csv`):

| Syndrome | Precision | Recall | F1 | Support |
|----------|----------:|-------:|---:|--------:|
| 心脾两虚证 | 0.000 | 0.000 | 0.000 | 3 |
| 热毒壅结证 | 0.000 | 0.000 | 0.000 | 3 |
| 阳虚痰凝证 | 0.000 | 0.000 | 0.000 | 2 |
| 血虚证 | 0.000 | 0.000 | 0.000 | 4 |
| 肾阳虚证 | 0.000 | 0.000 | 0.000 | 2 |
| 脾胃气虚证 | 0.000 | 0.000 | 0.000 | 6 |
| 肝肾亏损证 | 0.000 | 0.000 | 0.000 | 4 |
| 风热外袭证 | 0.000 | 0.000 | 0.000 | 3 |
| 风痰闭窍证 | 0.071 | 0.333 | 0.118 | 3 |
| 外伤损络证 | 0.083 | 0.250 | 0.125 | 4 |

Most frequent confusions (count ≥ 5):

| True | Predicted | Count |
|------|-----------|------:|
| 气虚血瘀证 | 气阴两虚证 | 64 |
| 气虚血瘀证 | 风痰瘀阻证 | 64 |
| 气虚血瘀证 | 瘀血阻络证 | 50 |
| 气虚血瘀证 | 痰瘀痹阻证 | 38 |
| 气虚血瘀证 | 阴虚血瘀证 | 36 |
| 肝肾亏虚证 | 气滞血瘀证 | 31 |
| 风痰瘀阻证 | 风痰上扰证 | 30 |
| 痰湿蕴肺证 | 风寒袭肺证 | 29 |
| 气虚血瘀证 | 痰瘀互结证 | 29 |
| 正虚瘀结证 | 正虚毒瘀证 | 26 |

## 6. Answers to the research questions

### Which model performed best?
**SVM (LinearSVC)** on validation (micro_f1=0.7517), and the locked test evaluation reached micro-F1=0.7548, macro-F1=0.4992.

### Did feature selection improve classification?
**Mixed.** Supervised selectors did not beat unsupervised variance truncation on average (negative mean Δ micro-F1 for MI / RF-importance / PCC-inspired). SVM gained from RF-importance (+micro/macro F1); Random Forest lost performance under several supervised filters at matched k=2000. Feature ranking remains useful for interpretability.

### Did advanced (deep) methods improve over traditional ML?
**No, not on this TCM-SD setup.** Huang-inspired CNN (val micro-F1=0.4635) and Chen-inspired BERT+CNN (val micro-F1=0.5007) both trailed LinearSVC and Random Forest. These were **adaptations** (virtual fields / frozen compact BERT; not exact paper reproductions) and lacked Huang’s 60 clinician fields and Chen’s constrained 21-label head.

### How do results answer the research question?
On public TCM-SD clinical text (chief complaint + description + four-exam notes) with a leakage-aware 70/10/20 split, traditional linear/margin models on train-fitted TF-IDF features classify 148 syndromes with test micro-F1 **0.7548** and macro-F1 **0.4992** for the selected SVM. Accuracy alone overstates rare-class quality: macro-F1 is substantially lower, matching the long-tailed label distribution.

### Limitations and future work
- TCM-SD is **multiclass**, not multi-label; Gong-style ML-PRDF was not faithfully applicable.
- Huang/Chen deep models were adapted under data/compute constraints; stronger GPU finetuning or true structured four-exam fields might change the deep vs classical gap.
- Char TF-IDF + engineered lengths are a proxy for symptoms, not a SymMap-normalized binary symptom vocabulary.
- Test was evaluated once after selection; further tuning on test is disallowed.
- Future work: calibrated probabilities, hierarchical TCM label constraints, multi-label corpora when licensed, and error-driven dictionary expansion for confused syndrome pairs.

## Artifact index

| Path | Role |
|------|------|
| `results/metrics/final_model_selection.json` | Locked validation decision |
| `results/metrics/final_integrity_report.json` | Leakage / overlap audit |
| `results/metrics/final_test_metrics.json` | Test metrics + model card |
| `results/metrics/final_test_summary.json` | Compact test summary |
| `results/metrics/final_test_per_class.csv` | Per-syndrome test P/R/F1 |
| `results/metrics/final_test_confusions.csv` | Frequent error pairs |
| `results/figures/final_*.png` | Comparison / confusion / worst-class plots |
| `docs/final_evaluation.md` | This report |
