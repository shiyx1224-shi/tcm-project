# Model comparison (validation)

Same frozen TCM-SD train/validation matrices and preprocessor for every model.
Task type: multiclass (one `norm_syndrome` per record). Test partition unused.

Primary ranking metric: validation accuracy. Best so far: **random_forest** (accuracy=0.7314, micro_f1=0.7314, macro_f1=0.4312).

## Differences

- **Random Forest** averages many shallow decision trees with `class_weight=balanced_subsample`. It can model non-linear interactions among TF-IDF / length features, which helps separate visually similar syndrome charts.
- **Logistic Regression** uses a linear multinomial decision boundary (`lbfgs`, L2, `class_weight=balanced`) in the same 5,000-D feature space. It is much smaller on disk than the RF ensemble but cannot capture higher-order feature interactions without explicit crosses.
- No multi-label wrapper (`MultiOutputClassifier` / `ClassifierChain`) was applied: the verified TCM-SD target is multiclass, not multi-label.

Accuracy gap (random_forest − logistic_regression): +0.2194.
Macro-F1 gap (random_forest − logistic_regression): +0.0996.

On this validation set, Random Forest is clearly stronger on accuracy, recall, micro-F1, and macro-F1. Weighted precision is similar for both (both near ~0.78), which suggests Logistic Regression often abstains from rare classes less cleanly—higher false negatives drag recall and F1.

Macro-F1 emphasizes rare syndromes; micro-F1 / accuracy weight frequent labels more heavily on this 148-class set.
