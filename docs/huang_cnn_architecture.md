# AdaptedCrossFGCNN — architecture notes

```
Input field_ids: (batch, 60) int64
        │
        ▼
Embedding(vocab, 16) → (batch, 60, 16)
        │
        ├──────────────────────────────┐
        ▼                              ▼
 flatten → (batch, 960)         transpose → (batch, 16, 60)
        │                              │
 CrossNetwork ×6                       Conv1d 16→14, k=4
 x ← x0⊙(xw)+b+x                       MaxPool1d ×2
        │                              tanh(Linear recomb on channels)
        │                              Conv1d 14→16, k=4 → pool → recomb
        │                              Conv1d 16→18, k=4 → pool → recomb
        │                              AdaptiveAvgPool1d(4) → flatten
        │                              Linear → 256  (= F)
        ▼                              │
   vector C (960)                      │
        │                              │
        └──────── concat ──────────────┘
                     │
                     ▼
            MLP: 1216 → 512 → 256 → 128 → 148 logits
                     │
                     ▼
              CrossEntropyLoss (class-weighted)
```

Parameter count is written into `artifacts/models/huang_cnn/validation_summary.json` after training.

**Not claimed:** Huang et al.’s published 96.21% dysmenorrhea accuracy — different data, fields, and label space.
