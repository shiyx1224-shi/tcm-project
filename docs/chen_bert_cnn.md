# Chen-inspired BERT + TextCNN (adaptation)

**Chosen parent paper:** Chen et al., 2024 — *Traditional Chinese medicine diagnostic prediction model for holistic syndrome differentiation based on deep learning* (Integrative Medicine Research). Model name in the paper: **TCM-BERT-CNN**.

**Why this paper (not Gong):** TCM-SD provides free-text clinical fields and a **single** `norm_syndrome` per row. That matches Chen’s **symptom text → syndrome** framing much better than Gong et al.’s **multi-label** Deep Forest + PCC-MLRF on binary symptom matrices. Gong’s ML-PRDF is **not** implemented here because a faithful multi-label deep forest would require multi-hot syndrome targets TCM-SD does not provide.

**Exact replication is not claimed.**

## Compatibility check

| Chen et al. 2024 element | TCM-SD support | Action |
|--------------------------|----------------|--------|
| Symptom / clinical **text** input | Yes (`chief_complaint`, `description`, `detection`) | Concatenate into one input string |
| BERT encoder + TextCNN | Methodologically compatible | Implement with a Chinese BERT |
| 21 holistic labels + Softmax pairs (exterior/interior, deficiency/excess) + Sigmoid group | **No** — 148 multiclass `norm_syndrome` | Multiclass Softmax head (adaptation) |
| Guideline/textbook expert-knowledge corpus | **No** — real TCM-SD clinical records | Document domain shift |
| 10-fold CV | Project uses frozen 70/10/20 | Same train/validation as RF/LR/SVM/Huang CNN |

## Architecture (adapted)

```
concat(chief_complaint, description, detection)
    → Chinese BERT tokenizer / encoder  (weights FROZEN — CPU adaptation)
    → last_hidden_state (B, T, H)
    → TextCNN (kernels 2,3,4,5) over token axis
    → max-over-time pool → concat channels
    → Dropout → Linear → Softmax over 148 syndromes
```

### From Chen et al.

- End-to-end **clinical text → syndrome** modeling  
- **BERT** contextual token embeddings  
- **TextCNN** over BERT sequence features for local n-gram patterns  
- Emphasis on **precision / recall / F1** under imbalance  
- Reported paper hyperparameter anchors: lr ~1e-5 for BERT finetuning, batch 20, dropout-style regularization (we adapt rates for the frozen-encoder setup)

### Adaptations (explicit)

1. **Frozen** compact Chinese BERT-family encoder (`hfl/rbt3`, 3-layer) with **online** forwards (full sequence embedding caches OOM on this CPU host). Full end-to-end finetuning of `bert-base-chinese` is also not practical here; `rbt3` keeps the BERT+CNN design while remaining runnable.  
2. Single **148-way Softmax** instead of Softmax constraint pairs + 17-way Sigmoid multi-label head.  
3. Same project **train/validation** split (not 10-fold CV).  
4. Class-weighted cross-entropy for long-tailed TCM-SD labels.  
5. No post-hoc symptom correlation matrices in this slice (Chen used them for interpretability).

## Research connection

The DS340W question asks how accurately models classify TCM syndromes from patient symptoms/clinical data. Chen operationalizes that as **deep text classification** of syndrome labels from symptom narratives. This experiment tests whether a BERT+CNN text model, adapted to TCM-SD’s multiclass EMR-style text, improves on (or complements) TF-IDF traditional ML and the Huang-inspired structured-field CNN.

## Validation metrics (this run)

| Metric | Value |
|--------|------:|
| Accuracy | 0.5007 |
| Precision (weighted) | 0.6411 |
| Recall (weighted) | 0.5007 |
| Micro-F1 | 0.5007 |
| Macro-F1 | 0.2521 |

Training curves: `results/figures/chen_bert_cnn_training_curves.png`.

Best checkpoint was epoch 2 (val accuracy 0.5007). Trails TF-IDF SVM/RF on this split; beats the Huang-inspired field CNN — consistent with Chen’s text-encoder emphasis when free text is the native input.

## Commands

```bash
pip install -r requirements-ml.txt
python scripts/train_chen_bert_cnn.py
python scripts/compare_models.py
```
