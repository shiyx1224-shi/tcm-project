# Model comparison (validation)

Same frozen TCM-SD train/validation matrices and preprocessor for every model.
Task type: multiclass (one `norm_syndrome` per record).
**Test partition was not used for model selection or ranking.**

Primary ranking metric: validation accuracy. Best so far: **svm** (accuracy=0.7517, micro_f1=0.7517, macro_f1=0.4745).

## Validation table

| model               | task_type   |   n_train |   n_validation |   n_features |   n_classes |   accuracy |   precision |   recall |   micro_f1 |   macro_f1 |   f1_weighted |   precision_macro |   recall_macro |
|:--------------------|:------------|----------:|---------------:|-------------:|------------:|-----------:|------------:|---------:|-----------:|-----------:|--------------:|------------------:|---------------:|
| svm                 | multiclass  |     37955 |           5420 |         5000 |         148 |   0.751661 |    0.818663 | 0.751661 |   0.751661 |   0.474519 |      0.771185 |          0.437624 |       0.578806 |
| random_forest       | multiclass  |     37955 |           5420 |         5000 |         148 |   0.731365 |    0.783299 | 0.731365 |   0.731365 |   0.431199 |      0.741544 |          0.440277 |       0.467479 |
| logistic_regression | multiclass  |     37955 |           5420 |         5000 |         148 |   0.511993 |    0.776272 | 0.511993 |   0.511993 |   0.331595 |      0.558667 |          0.303568 |       0.515102 |
| chen_bert_cnn       | multiclass  |     37955 |           5420 |           96 |         148 |   0.500738 |    0.641123 | 0.500738 |   0.500738 |   0.252063 |      0.504471 |          0.272675 |       0.324034 |
| huang_cnn           | multiclass  |     37955 |           5420 |           60 |         148 |   0.463469 |    0.612459 | 0.463469 |   0.463469 |   0.211236 |      0.472268 |          0.195517 |       0.29422  |

![Validation metric comparison](results/figures/model_comparison.png)

## Algorithm notes

- **Random Forest** — non-linear ensemble of trees; `class_weight=balanced_subsample`.
- **Logistic Regression** — linear multinomial classifier (`lbfgs`, balanced).
- **SVM** — linear support-vector classifier (`LinearSVC`, OvR, balanced).
- **Huang-inspired CNN** — AdaptedCrossFGCNN (cross network + FGCNN-style CNN); **not** an exact reproduction of Huang et al. 2022 (different data/fields/labels).
- **Chen-inspired BERT+CNN** — frozen Chinese BERT + TextCNN multiclass head; **not** an exact reproduction of Chen et al. 2024 TCM-BERT-CNN (no Softmax-pair / Sigmoid multi-label constraint head; frozen encoder).

## Ranking (validation accuracy)

1. **SVM (LinearSVC)** — accuracy=0.7517, precision=0.8187, recall=0.7517, micro_f1=0.7517, macro_f1=0.4745
2. **Random Forest** — accuracy=0.7314, precision=0.7833, recall=0.7314, micro_f1=0.7314, macro_f1=0.4312
3. **Logistic Regression** — accuracy=0.5120, precision=0.7763, recall=0.5120, micro_f1=0.5120, macro_f1=0.3316
4. **Chen-inspired BERT+CNN** — accuracy=0.5007, precision=0.6411, recall=0.5007, micro_f1=0.5007, macro_f1=0.2521
5. **Huang-inspired CNN** — accuracy=0.4635, precision=0.6125, recall=0.4635, micro_f1=0.4635, macro_f1=0.2112

**Conclusion:** Among the three traditional ML algorithms trained so far, **SVM (LinearSVC)** performs best on the validation set and is the preferred baseline before any deep-learning work. The held-out test set remains sealed.
