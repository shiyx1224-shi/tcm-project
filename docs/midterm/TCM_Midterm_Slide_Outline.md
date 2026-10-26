# DS 340W Midterm — Slide-by-Slide Outline

Editable deck: [`TCM_Midterm_Presentation.pptx`](./TCM_Midterm_Presentation.pptx)  
Script: [`TCM_Midterm_Speaking_Script.md`](./TCM_Midterm_Speaking_Script.md)  
Theme: rice `#F5F1E8`, herbal `#426653`, ink `#27362D`, wood `#956F4D`, cinnabar `#A6483E`

All numbers below are verified against `results/metrics/` in the repo (audit re-score matched test accuracy **0.754848…**).

---

## Section A — Background & parent papers (0:00–5:00)

### Slide 1 — Title (~0:30)
- **Purpose:** Introduce course presentation, RQ, and public links.
- **On slide:** Chinese/English title; DS 340W; GitHub + website URLs.
- **Say:** Who you are, what the talk covers (5 min literature / 5 min your work).
- **Do not:** Dive into metrics yet.

### Slide 2 — TCM background (~1:00)
- **Purpose:** Level-set non-TCM classmates.
- **Bullets:** TCM whole-person view; 辨证; four exams; why ML is hard.
- **Visual idea:** Keep text sparse; one concept per line.
- **Say:** Syndromes ≠ Western disease labels; data are noisy free text.

### Slide 3 — Research question & motivation (~0:45)
- **Purpose:** State the exact RQ and *why* it matters scientifically.
- **On slide:** Full RQ in a card; three motivation bullets.
- **Say:** Public reproducibility + classical vs deep comparison—not “build an AI doctor.”

### Slide 4 — Gong et al. 2023 (~0:55)
- **Citation:** Frontiers in Genetics; doi:10.3389/fgene.2023.1272016
- **Cover:** Multi-label goal; feature ranking / deep forest spirit; influence on FS.
- **Must say:** TCM-SD is **multiclass** → not a full multi-label reproduction.

### Slide 5 — Huang et al. 2022 (~0:55)
- **Citation:** JMIR Med Inform; doi:10.2196/29290
- **Cover:** Cross-FGCNN; 60 fields; feature interactions; your AdaptedCrossFGCNN.
- **Must say:** Adaptation on free text / virtual fields—not their private EMR corpus.

### Slide 6 — Chen et al. 2024 + synthesis (~0:55)
- **Citation:** Integr Med Res; doi:10.1016/j.imr.2023.101019
- **Cover:** Holistic DL / BERT+CNN idea; three-card Gong–Huang–Chen map.
- **Transition sentence:** “That literature led me to one shared public benchmark…”

---

## Section B — Your project (5:00–10:00)

### Slide 7 — Dataset & preprocessing (~1:00)
- **Dataset:** TCM-SD · https://github.com/Borororo/ZY-BERT · CC BY-NC-SA 4.0
- **Facts:** 54,152 rows; 148 labels; inputs `chief_complaint|description|detection`
- **Split:** 70/10/20 leakage-aware → 37,955 / 5,420 / 10,777
- **Features:** train-only TF-IDF + SelectKBest χ² k=5000
- **Show:** Public link large enough to read on Zoom.

### Slide 8 — ML methodology (~1:10)
- **Workflow graphic:** Dataset → Preprocess → Features → Train → Validate → Test once
- **Models verified in repo:** RF, LR, Linear SVM, FS ablation, Huang-inspired CNN, Chen-inspired BERT+CNN
- **Protocol:** val micro-F1 selection; test once
- **Clarify:** Website Explorer ≠ trained SVM

### Slide 9 — Results (~0:55)
- **Validation leaderboard (micro-F1):** SVM 0.7517 > RF 0.7314 > LR 0.5120 > Chen 0.5007 > Huang 0.4635
- **Test (selected SVM, n=10,777):** Acc/Micro-F1 **0.7548**; Macro-F1 **0.4992**
- **Takeaways:** Deep adaptations lagged; FS mixed; rare classes hurt macro-F1
- **Figure:** `results/figures/model_comparison.png` embedded in PPTX

### Slide 10 — Contribution (~0:55)
- Shared public benchmark + leakage-aware pipeline
- Fair classical vs adapted-deep comparison
- Honest deviations from parent papers
- Website separates ML results from teaching demo
- **Not claimed:** new SOTA architecture; exact paper reproduction

### Slide 11 — Future work & conclusion (~1:00)
- Rare-class / macro-F1; hierarchical constraints; richer Chinese NLP
- True multi-label only if licensed data appears
- Close by restating RQ answer so far (~75% micro-F1; rare syndromes remain hard)
- Thank you + GitHub

---

## Zoom readability checklist

- [ ] Share entire screen or PPT window at 100% zoom  
- [ ] Fonts ≥ 18 pt body / ≥ 28 pt titles (deck uses ~19–30)  
- [ ] Do not scroll dense README live—use these slides  
- [ ] Keep Explorer demo optional; if shown, say “teaching only” first  

---

## Evidence map (claim → file)

| Claim | Source |
|-------|--------|
| 54,152 / 148 | `DATASET.md`, local TCM-SD load |
| 70/10/20 sizes | `artifacts/preprocess/partition_summary.csv` |
| Val leaderboard | `results/metrics/model_comparison.csv` |
| Test 0.7548 | `results/metrics/final_test_metrics.json` |
| SVM selected on val only | `results/metrics/final_model_selection.json` |
| Adaptations documented | `docs/huang_cnn.md`, `docs/chen_bert_cnn.md`, `docs/parent_papers.md` |
