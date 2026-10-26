# Huang-inspired CNN (AdaptedCrossFGCNN)

**Inspiration:** Huang et al., 2022 — *A traditional Chinese medicine syndrome classification model based on cross-feature generation by convolution neural network* (JMIR Medical Informatics; Cross-FGCNN).

**This repository does not claim exact reproduction.** Huang’s dysmenorrhea EMR corpus, 60 standardized TCM diagnostic fields, and 9-class label set are not available here.

## Does TCM-SD support Huang’s setup?

| Huang et al. 2022 requirement | TCM-SD available? | Implication |
|------------------------------|-------------------|-------------|
| 60 structured four-exam symptom **fields** | **No** — free text (`chief_complaint`, `description`, `detection`) | Must invent a field-like encoding |
| One-hot / categorical field values | **No** | Use character-position slot IDs → embeddings |
| 9 dysmenorrhea syndromes | **No** — **148** `norm_syndrome` classes | Multiclass head widened |
| Single-disease dysmenorrhea cohort | **No** — mixed clinical records | Different label prior / difficulty |
| Public tabular dump of their 5,273 cases | **No** | Train only on authorized TCM-SD |

**Feasible to adapt:** multiclass syndrome classification + embedding + **cross network** + **CNN recombination** + MLP + cross-entropy, on the **same train/validation partitions** as RF / LR / SVM.

## Architecture (adapted)

```
TCM-SD text (3 columns)
    → 60 virtual character-position slots (20 per column)
    → Embedding (dim 16)
        ├─ flatten → CrossNetwork (6 layers) → vector C
        └─ FGCNN branch (3× Conv1d/pool/tanh-recomb) → vector F
    → concat(C, F) → MLP 512/256/128 → Softmax over 148 syndromes
```

### From Huang et al. (methodological elements kept)

1. Field-style **embeddings** as the model input representation  
2. **Cross network** for explicit higher-order linear feature crosses (paper: 6 layers)  
3. **FGCNN-style** nonlinear branch: convolution → max pooling → FC+tanh recombination (3 stages; paper depths 14/16/18, kernel width 4)  
4. **Concatenate** linear-cross features \(C\) with nonlinear features \(F\)  
5. MLP classifier, **dropout 0.2**, **Adam lr=0.001**, **cross-entropy**

### Adaptations (explicit)

1. **60 virtual slots** sampled from free-text characters — *not* Huang’s 60 TCM diagnostic fields  
2. **148-class** TCM-SD head instead of 9 dysmenorrhea labels  
3. MLP widths **512/256/128** (paper 1024/512/128) for CPU training  
4. **Class-weighted** cross-entropy for long-tailed labels  
5. Epoch training with **best-validation checkpoint** (paper described 1000 iterations on their data)

## Commands

```bash
pip install -r requirements.txt
python scripts/train_huang_cnn.py --epochs 8
python scripts/compare_models.py
```

## Validation metrics (this run)

| Metric | Value |
|--------|------:|
| Accuracy | 0.4635 |
| Precision (weighted) | 0.6125 |
| Recall (weighted) | 0.4635 |
| Micro-F1 | 0.4635 |
| Macro-F1 | 0.2112 |
| Log-loss | 2.1075 |

Training curves: `results/figures/huang_cnn_training_curves.png`.

## Comparison vs traditional ML (same validation rows)

| Model | Accuracy | Micro-F1 | Macro-F1 |
|-------|---------:|---------:|---------:|
| SVM | **0.7517** | **0.7517** | **0.4745** |
| Random Forest | 0.7314 | 0.7314 | 0.4312 |
| Logistic Regression | 0.5120 | 0.5120 | 0.3316 |
| Huang-inspired CNN | 0.4635 | 0.4635 | 0.2112 |

On TCM-SD, the adapted CNN trails the TF-IDF traditional baselines. That gap is expected: Huang’s method was designed for **structured 60-field dysmenorrhea charts**, while this adaptation compresses free text into 60 virtual slots (~1.5M parameters) without the paper’s clinician-coded fields. **Do not treat this as Huang’s published 96% result.**

## Artifacts

| Path | Contents |
|------|----------|
| `artifacts/models/huang_cnn/huang_cnn.pt` | Weights + config |
| `artifacts/models/huang_cnn/validation_*.json` | Metrics |
| `artifacts/models/huang_cnn/training_history.json` | Per-epoch curves data |
| `results/figures/huang_cnn_training_curves.png` | Loss / accuracy curves |
| `docs/huang_cnn_architecture.md` | Module diagram + shapes |

Same split policy: validation for reporting / checkpointing; **test unused**.
