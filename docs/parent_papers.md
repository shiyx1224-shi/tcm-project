# Parent papers — research foundation (DS 340W)

**Research question:** How accurately can machine learning models classify TCM syndromes based on patients’ symptoms and clinical data?

**Scope of this document:** Verified methodology analysis only. No models are implemented here.

**Source materials used:** The three PDFs supplied in this project’s upload folder were extracted and checked against the published bibliographic records. Copyrighted PDFs are **not** committed to the repository; cite the DOIs below.

| Upload file (local) | Verified paper |
|---------------------|----------------|
| `ds340w parent paper.pdf` / `ds340w_parent_paper_b183.pdf` | Gong et al., 2023 |
| `ds340w parent paper 2.pdf` / `ds340w_parent_paper_2_6ed5.pdf` | Huang et al., 2022 (**confirmed**) |
| `ds340w parent paper 3.pdf` / `ds340w_parent_paper_3_f53c.pdf` | Chen et al., 2024 |

If any future paper swap is needed, re-supply the full PDF (or a complete open-access text). Do not rely on title guesses alone.

---

## Paper A — Huang et al., 2022 (confirmed parent)

### Citation

Huang Z, Miao J, Chen J, Zhong Y, Yang S, Ma Y, Wen C. A traditional Chinese medicine syndrome classification model based on cross-feature generation by convolution neural network: model development and validation. *JMIR Medical Informatics*. 2022;10(4):e29290.  
https://doi.org/10.2196/29290 · PMID available via publisher page · Open access (CC BY 4.0)

### Actual dataset and source

| Item | Verified detail |
|------|-----------------|
| Disease focus | Dysmenorrhea |
| Size | **5,273** cases |
| Composition | **4,000** high-quality EMRs from the **Sichuan TCM big data management platform** + **1,273** dysmenorrhea cases from the **Chinese literature database** |
| Quality control | Two professional TCM doctors verified records against TCM standards |
| Feature form after prep | Structured into **60 fields** following the four examinations (inspection, listening/smelling, inquiry, palpation); symptoms standardized then mapped into fields (e.g., white tongue coating → coating-color field) |
| Label space | **9** syndrome types (uneven class counts; see Table 2 in paper) |
| Split | Random **3:1** train/test (75% / 25%) |
| Public release | **Not** released as a downloadable CSV in the paper. Acknowledgments name Sichuan TCM big data management platform as the main source. |

**Nine syndrome classes (exact paper wording / labels):**  
liver-kidney depletion; pattern of congealing cold with blood stasis; cold-dampness stagnation; liver constraint and dampness-heat; deficiency of qi and blood; qi stagnation and blood stasis; kidney deficiency and blood stasis; dampness-heat stasis obstruction; yang deficiency and internal cold.

### Classification problem

- **Task type:** Multiclass syndrome classification for a **single disease** (dysmenorrhea).
- **Input:** High-dimensional, sparse, field-structured four-examination symptom/sign data (label-encoded 60-dimensional field vector → one-hot per field → embedding).
- **Output:** One of nine dysmenorrhea syndrome types.
- **Core difficulty the paper targets:** Missing values and sparsity in TCM EMRs; flat symptom vectors ignore that signs belong to diagnostic fields.

### Model architecture and feature handling

**Model name:** Cross-FGCNN (cross-feature generation by CNN).

**Pipeline (four modules):**

1. **Data embedding** — map symptoms into TCM diagnostic fields; one-hot per field; dense embedding to a shared low-dimensional representation.
2. **Linear cross feature module** — **Cross network** (paper uses **6** cross layers) to build higher-order *linear* feature crosses while preserving residual-style carry of earlier signals.
3. **Nonlinear feature module** — **FGCNN**: convolution → max pooling → recombination (fully connected + tanh), repeated (**3** convolution stages with kernel depths 14/16/18, width 4); flatten into MLP to get local + global nonlinear crosses.
4. **Classification** — concatenate linear vector \(C\) and nonlinear vector \(F\); MLP (**1024 / 512 / 128**); multiclass decision with **cross-entropy** loss.

**Training hyperparameters reported:** dropout 0.2; learning rate 0.001; 1000 iterations.

**Feature selection:** Not Relief/filter selection. Instead: **TCM-guided field segmentation (60 fields)** + learned linear/nonlinear **cross features** (inspired by CTR models such as DCN / FGCNN).

**Baselines compared:** Bayesian, ML-KNN, 10-layer ANN, decision tree, (hypergraph / spectral) clustering, SVM; plus CTR-style DNN, FGCNN, and Deep & Cross Network (DCN).

### Evaluation metrics

Reported for Cross-FGCNN and baselines:

- **Accuracy** (overall; Cross-FGCNN **96.21%**)
- **F1 score** (Cross-FGCNN **0.9621**)
- **Confusion matrix**
- **Log-loss**
- **ROC curves** / area under macro-average ROC (emphasized because rare syndromes exist)

### How to adapt this methodology (without claiming their accuracy)

1. Structure any symptom set into **four-examination fields** (even a reduced field list is fine for a course project).
2. Treat sparsity explicitly: allow missing tongue/pulse fields; prefer models that learn **feature interactions** (cross layers, factorization machines, or CNN over field embeddings) rather than only independent symptom indicators.
3. For a dysmenorrhea-like lens, use a **closed multiclass label set** of the nine pattern families above (or a documented subset).
4. Evaluate with accuracy **and** F1, confusion matrix, and class-aware curves/log-loss — not accuracy alone on imbalanced labels.
5. **Data gap:** Their 5,273 EMR+literature corpus is not public. For DS340W, either (a) request/partner data, (b) build a **teaching/synthetic** chart set with the same field schema and nine labels, or (c) use another public TCM dysmenorrhea resource and document the mismatch.

---

## Paper B — Gong et al., 2023 (second parent; verified from upload)

### Citation

Gong L, Jiang J, Chen S, Qi M. A syndrome differentiation model of TCM based on multi-label deep forest using biomedical text mining. *Frontiers in Genetics*. 2023;14:1272016.  
https://doi.org/10.3389/fgene.2023.1272016 · Open access (CC BY)

### Actual dataset and source

| Item | Verified detail |
|------|-----------------|
| Disease foci | **Kidney disease** and **stomach disease** (separate experiments) |
| Kidney | **645** cases; **755** symptom features; **124** syndrome labels; source: National Population Health Science Data Centre **PHDA** TCM Prevention and Control of Chronic Renal Failure database |
| Stomach | **436** cases; **323** symptom features; **49** syndrome labels; source: TCM outpatient diagnosis/treatment records (desensitized) |
| Access claimed by authors | https://www.ncmi.cn/index.htm and https://github.com/web333panda/TCM-Dataset |
| Preprocessing | Drop records missing syndromes or symptoms; combine single-label records into multi-label records; synonym merge via a dictionary grounded in **SymMap** (Wu et al., 2019) |

**Note for the project:** Re-check that the GitHub/NCMI links still resolve and that license/terms allow course use. If the repo is gone, you must supply a replacement dump or another authorized kidney/stomach multi-label chart set.

### Classification problem

- **Task type:** **Multi-label** syndrome differentiation (a case can carry **two or more** syndromes).
- **Input:** Binary/standardized symptom feature vectors after dictionary normalization.
- **Output:** Subset of syndrome labels (kidney: up to 124 label vocabulary; stomach: 49).
- **Core difficulties:** Multi-syndrome combination; **small** non-standard corpora; high-dimensional redundant symptoms.

### Model architecture and feature selection

**Model name:** **ML-PRDF** = multi-label deep forest (**MLDF**) + **PCC-MLRF** feature selection.

1. **PCC-MLRF (feature selection)**  
   - Starts from multi-label ReliefF (ML-ReliefF).  
   - Replaces cosine-only sample similarity with a **Pearson correlation–based** similarity (authors use reciprocal of Pearson distance).  
   - Traverses samples (not random sampling) when updating feature weights.  
   - Outputs features ranked by weight; top features feed the classifier (paper illustrates top-40 weights).

2. **MLDF (classifier)**  
   - Cascade of multi-label forests (representation learning without needing DNN-scale data).  
   - Uses multi-label forest ensembles (including RF-PCT-style predictive clustering trees) with measure-aware feature reuse and layer growth.  
   - Final multi-label decision via thresholding of per-label scores (thresholding / TCM-aware scoring described in the paper’s process figure).

**Comparators:** Label Powerset, ML-KNN, BP-MLL; feature-selection ablations vs PCA, variance filtering, classic ML-ReliefF; also BR and Classifier Chains in the feature-selection study.

### Evaluation metrics

**Primary multi-label ranking/set metrics (↓ lower better where noted):**

- Hamming loss ↓  
- One-error ↓  
- Coverage ↓  
- Ranking loss ↓  
- Average precision ↑  

Also used in feature-selection comparisons: mlACC, mlPRE, mlREC, mlF1, subset ACC; Macro-AUC / per-syndrome AUC discussed for common CRF patterns (e.g., damp turbidity, spleen-kidney yang/yin deficiency, liver-kidney yin deficiency).

**Validation:** **5-fold** cross-validation for the model comparisons reported in Tables 4–6.

**Example headline results (from paper Tables 4–5; do not treat as your project’s accuracy):**  
Kidney ML-PRDF average precision **0.5168 ± 0.0085**; stomach ML-PRDF average precision **0.6014 ± 0.0105**, with best/near-best Hamming, coverage, ranking loss among listed baselines.

### How to adapt this methodology

1. Frame the research question as **multi-label** whenever charts can carry coexisting syndromes.
2. Build or reuse a **symptom synonym dictionary** before modeling.
3. Run a **filter-style multi-label feature ranking** (PCC-MLRF or a simpler Relief/mutual-information multi-label proxy) before the classifier — especially on small \(n\), large \(p\) data.
4. Prefer small-data-friendly multi-label learners (ML-kNN, classifier chains, random-forest cascades) before large deep nets.
5. Report **Hamming / one-error / AP** (and subset accuracy if useful), not single-label accuracy alone.
6. **Data path:** Try the authors’ GitHub dataset first; document exact commit/hash and schema. If unavailable, say so and substitute an authorized multi-label chart set with the same evaluation protocol.

---

## Paper C — Chen et al., 2024 (third parent; verified from upload)

### Citation

Chen Z, Zhang D, Liu C, Wang H, Jin X, Yang F, Zhang J. Traditional Chinese medicine diagnostic prediction model for holistic syndrome differentiation based on deep learning. *Integrative Medicine Research*. 2024;13:101019.  
https://doi.org/10.1016/j.imr.2023.101019 · Open access (CC BY-NC-ND)

### Actual dataset and source

| Item | Verified detail |
|------|-----------------|
| Nature of data | **Expert-knowledge dataset** built from TCM **clinical practice guidelines / expert consensus** and **textbooks** (e.g., Internal Medicine, Pediatrics, Gynecology in TCM) — **not** a hospital EMR dump of a single disease |
| Literature search bases | CNKI, Wanfang, VIP, SinoMed, PubMed, Embase, etc., inception–2022; dual TCM-background screeners + third-party consensus |
| Size | **6,148** samples (multiple syndromes can coexist / intersect in one sample) |
| Label space | **21** holistic syndromes |
| Label groups | (1) Eight-principle style: exterior, interior, deficiency, excess, cold, heat; (2) Zang: heart, liver, spleen, lung, kidney; (3) Pathology: excess cold, deficiency cold, deficiency heat, excess heat, qi deficiency, blood deficiency, qi stagnation, blood stasis, phlegm fluid retention, critical |
| Normalization refs | WHO International Standard Terminologies on TCM; Standardization of Common Clinical Symptom Terminology in TCM; *TCM Diagnosis* textbook; Clinical Terminology in TCM; Classification and Coding of TCM Diseases and Syndromes |
| Public release | “Available within the article and from the corresponding author upon reasonable request” — **not** a guaranteed public CSV |

Class counts are highly imbalanced (e.g., exterior **362** vs interior **5,786**).

### Classification problem

- **Task type:** **Holistic** multi-syndrome prediction across diseases (not “syndromes under one Western/TCM disease name”).
- **Input:** Symptom text (end-to-end text classification: symptom input → syndrome output).
- **Output:** Predictions over 21 syndromes with **TCM classification constraints**.
- **Core difficulty:** Single-disease models miss holistic differentiation; syndromes co-occur; minority classes are fragile if only accuracy is used.

### Model architecture and feature handling

**Model name:** **TCM-BERT-CNN**.

- **BERT** encodes symptom text (token / segment / position embeddings).  
- **TextCNN** refines BERT embeddings into N-gram / local features.  
- **Constraint design:**  
  - Constrained pairs: **exterior vs interior**; **deficiency vs excess** (binary heads with **Softmax** so probabilities sum to 1).  
  - Remaining **17** syndromes: overall multi-label-style group with **Sigmoid**.  
- Hyperparameters reported: learning rate **1e-5**, batch size **20**, **20** epochs; PyTorch 1.10 / Python 3.6.  
- Baselines: BERT, TextCNN, LSTM RNN, LSTM-attention.

**Feature selection:** No classic filter selector. Features are **learned semantic embeddings** plus post-hoc **symptom correlation matrices** for interpretability (e.g., deficiency, cold, excess heat, qi deficiency).

### Evaluation metrics

Because of imbalance, authors **reject accuracy as primary** and report:

- **Precision**
- **Recall**
- **F1 score**

Overall TCM-BERT-CNN (10-fold CV, Table 1): precision **0.926 ± 0.0274**, recall **0.9238 ± 0.0293**, F1 **0.9247 ± 0.0239**.

**Validation:** **Ten-fold** cross-validation.

### How to adapt this methodology

1. Add a **holistic label layer** (principles / zang / pathology) even if disease-specific models are also trained.
2. Encode **mutual exclusion constraints** (exterior–interior, deficiency–excess) in the head or as post-processing penalties.
3. Prefer **precision / recall / F1** (macro and per-label) under imbalance; optionally add Hamming/AP if labels are multi-hot.
4. Keep a **symptom co-occurrence / correlation view** for interpretability (matches TCM “key signs travel together”).
5. **Data gap:** This is guideline/textbook-derived text, not EMR. For DS340W, either request authors’ data, reconstruct a transparent teaching set from cited standards (document every source), or clearly separate “expert-knowledge simulation” from “clinical EMR classification.”

---

## Methodology comparison (side by side)

| Dimension | Huang 2022 | Gong 2023 | Chen 2024 |
|-----------|------------|-----------|-----------|
| **RQ fit** | Accuracy of syndrome class given symptoms (single disease) | Accuracy/quality of **multi-label** syndrome sets on small clinical texts | Accuracy of **holistic** multi-syndrome prediction from symptom text |
| **Data type** | Real dysmenorrhea EMRs + literature cases | Real kidney + stomach clinical records | Guideline/textbook expert-knowledge samples |
| **n** | 5,273 | 645 kidney; 436 stomach | 6,148 |
| **Labels** | 9 multiclass | 124 / 49 multi-label | 21 multi-aspect (constrained + sigmoid groups) |
| **Structure** | 60 four-exam fields | Flat symptom features after SymMap-style dict | Free symptom text → BERT tokens |
| **Key method** | Cross network + FGCNN | PCC-MLRF + multi-label deep forest | BERT + CNN + Softmax/Sigmoid constraints |
| **Feature strategy** | Field embedding + learned crosses | Explicit multi-label Relief-style selection | Learned embeddings + correlation viz |
| **Primary metrics** | Acc, F1, log-loss, ROC | Hamming, one-error, coverage, ranking loss, AP | Precision, recall, F1 |
| **Validation** | 75/25 random split | 5-fold CV | 10-fold CV |
| **Public data?** | No public dump in paper | Authors point to NCMI + GitHub TCM-Dataset | On request / within article |

### Shared methodological lessons for the DS340W project

1. **Define the task type explicitly** in the research question write-up: multiclass (Huang), multi-label (Gong), holistic constrained multi-output (Chen). “How accurately…” must name which label scheme you mean.
2. **Standardize symptoms** before learning (fields, dictionaries, or controlled terminology).
3. **Do not rely on accuracy alone** when classes are rare or multi-label.
4. **Respect TCM structure**: four examinations (Huang), coexisting syndromes (Gong), principle constraints (Chen).
5. **Separate claimed parent-paper metrics from your own results.** Their published numbers are not transferable without the same data and protocol.

### What you still need to supply before modeling

| Need | Why |
|------|-----|
| **Authorized training data** matching at least one paper’s setting (or a documented teaching substitute) | Huang’s Sichuan EMR set is closed; Chen’s set is request-only; Gong’s GitHub must be re-verified |
| **Frozen label ontology** (which syndromes, multiclass vs multi-label) | The three papers answer slightly different classification problems |
| **Evaluation plan** tied to that ontology | Copy Huang metrics for multiclass; Gong metrics for multi-label; Chen metrics for imbalanced holistic labels |
| **Nothing further on paper identity** | All three uploaded PDFs were readable and match the citations above |

---

## Mapping to the research question

> How accurately can machine learning models classify TCM syndromes based on patients’ symptoms and clinical data?

| Paper | How it operationalizes “accurately” | How it operationalizes “symptoms and clinical data” |
|-------|--------------------------------------|------------------------------------------------------|
| Huang | Acc / F1 / ROC / log-loss on held-out dysmenorrhea cases | Field-structured four-exam EMR + literature charts |
| Gong | Multi-label ranking/set losses and AP under 5-fold CV | Standardized symptom vectors from kidney/stomach records |
| Chen | Precision / recall / F1 under 10-fold CV | Symptom text derived from guidelines/textbooks (expert knowledge as clinical standards) |

A coherent DS340W design can **borrow methods from all three** (field structure + multi-label evaluation + holistic constraints) while **training only on data you are allowed to use**, and must state which operationalization of “accuracy” you report.

---

## Document control

- Written from full-text extraction of the three uploaded PDFs (Huang 16 pp., Gong 10 pp., Chen 7 pp.).
- No model training, no re-implementation, and no claim that parent-paper accuracies apply to this repository’s teaching charts.
