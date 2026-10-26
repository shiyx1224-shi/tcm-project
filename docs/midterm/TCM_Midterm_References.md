# DS 340W Midterm — References & Likely Q&A

## Full citations (use in speaker notes / handout)

### Parent papers

1. Gong L, Jiang J, Chen S, Qi M. A syndrome differentiation model of TCM based on multi-label deep forest using biomedical text mining. *Frontiers in Genetics*. 2023;14:1272016. https://doi.org/10.3389/fgene.2023.1272016

2. Huang Z, Miao J, Chen J, Zhong Y, Yang S, Ma Y, Wen C. A traditional Chinese medicine syndrome classification model based on cross-feature generation by convolution neural network: model development and validation. *JMIR Medical Informatics*. 2022;10(4):e29290. https://doi.org/10.2196/29290

3. Chen Z, Zhang Y, Liu H, et al. Traditional Chinese medicine diagnostic prediction model for holistic syndrome differentiation based on deep learning. *Integrative Medicine Research*. 2024. https://doi.org/10.1016/j.imr.2023.101019

### Dataset & benchmark

4. Ren M, Huang H, Zhou Y, Cao Q, Bu Y, Gao Y. TCM-SD: A Benchmark for Probing Syndrome Differentiation via Natural Language Processing. In: *Proceedings of the 21st Chinese National Conference on Computational Linguistics (CCL 2022)*. 2022:908–920. https://aclanthology.org/2022.ccl-1.80/

5. Public packaging / download page used in this project: https://github.com/Borororo/ZY-BERT  
   Dataset license documented in-repo as **CC BY-NC-SA 4.0** (see `DATASET.md`).

### Project artifacts

6. Project repository: https://github.com/shiyx1224-shi/tcm-project  
7. Live site: https://shiyx1224-shi.github.io/tcm-project/  
8. Measured results: `results/metrics/model_comparison.csv`, `results/metrics/final_test_metrics.json`, `docs/final_evaluation.md`

---

## Compact slide citations (already on PPTX footers)

| Slide | Short cite |
|-------|------------|
| 4 | Gong et al., 2023 · doi:10.3389/fgene.2023.1272016 |
| 5 | Huang et al., 2022 · doi:10.2196/29290 |
| 6 | Chen et al., 2024 · doi:10.1016/j.imr.2023.101019 |
| 7 | TCM-SD via Borororo/ZY-BERT · Ren et al., CCL 2022 |

---

## Five realistic Q&A prompts (with short answers)

### 1) Dataset — “Is your data public, and can I reproduce the download?”

**Answer:** Yes. I use **TCM-SD** from **https://github.com/Borororo/ZY-BERT** (CC BY-NC-SA 4.0). My README/`DATASET.md` and `scripts/download_tcm_sd.sh` document the exact files. Locally I load **54,152** records and **148** `norm_syndrome` labels. Parent-paper hospital corpora are **not** public, which is why I standardized on TCM-SD.

### 2) Model selection — “Why did you pick SVM as the final model?”

**Answer:** I trained multiple models on the **same** leakage-aware split and chose by **validation micro-F1 only**. SVM was highest at **0.7517**. Only after that lock did I score the held-out test set once (**0.7548** micro-F1 / accuracy). Test was not used for selection (`final_model_selection.json`).

### 3) Results — “Your deep models underperformed—does that mean deep learning fails for TCM?”

**Answer:** Not globally. It means **on this public multiclass text setup**, with my **adapted** Huang/Chen architectures (virtual fields; frozen compact BERT), classical TF-IDF + Linear SVM / RF won. Their original papers used different data (structured fields / different label heads). Macro-F1 ≈ **0.50** also shows rare syndromes remain hard even when micro-F1 looks good.

### 4) Novelty — “What makes your project different from the three parent papers?”

**Answer:** I don’t claim a new SOTA network. My contribution is a **reproducible shared-benchmark study**: classical baselines + parent-inspired **adaptations**, leakage-aware 70/10/20 splits, feature-selection ablations, and a locked test. I also keep a hard distinction between the **ML evaluation** and the website’s **educational teaching-pattern desk**.

### 5) Future work — “What would you do next if you had more time?”

**Answer:** Focus on **rare-class / macro-F1** improvements, richer Chinese clinical text features, hierarchical TCM constraints, and error analysis on frequent confusions. I’d only move to Gong-style **multi-label** methods if I obtain a properly licensed multi-label corpus—TCM-SD itself is single-label.

---

## Quick “don’t say this” list

- Don’t say the teaching Explorer “is my trained SVM.”  
- Don’t say you “exactly reproduced” Gong/Huang/Chen.  
- Don’t quote parent-paper hospital accuracies as your results.  
- Don’t mix validation and test numbers when answering “what’s your accuracy?”
