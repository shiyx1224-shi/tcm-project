# DS 340W Midterm — Complete 10-Minute Speaking Script

**Title:** Traditional Chinese Medicine Syndrome Classification Using Machine Learning  
**Target length:** ~10:00 (≈1,250–1,300 spoken words)  
**Slides:** `TCM_Midterm_Presentation.pptx` (11 slides)  
**Repo:** https://github.com/shiyx1224-shi/tcm-project  
**Site:** https://shiyx1224-shi.github.io/tcm-project/

Practice tip: read aloud once with a timer. Aim for calm pacing—about 125–130 words per minute.

---

## Slide 1 — Title (~0:30) · words ≈ 70

Hi everyone—I’m presenting my DS 340W research project: **Traditional Chinese Medicine Syndrome Classification Using Machine Learning**.

My research question is: *How accurately can machine learning models classify TCM syndromes based on patients’ symptoms and clinical data?*

Everything I’ll show is in my public GitHub repo and on the project website. I’ll spend the first five minutes on background and three parent papers, then five minutes on my own pipeline, results, and contribution.

---

## Slide 2 — TCM background (~1:00) · words ≈ 145

For classmates who haven’t studied Traditional Chinese Medicine: TCM doesn’t only name a Western disease. It tries to describe a **pattern** of imbalance—what TCM calls a **syndrome**.

**Syndrome differentiation**, or 辨证, means reading symptoms and signs together and deciding which pattern fits—things like qi deficiency, damp-heat, or blood stasis. Clinicians traditionally use the **four examinations**: looking, listening and smelling, asking, and pulse/palpation.

That sounds structured, but the data are messy. Notes are free text. Two syndromes can look alike. Tongue and pulse fields are often sparse. And some labels are rare. So even experienced people disagree, and for machine learning this is a hard multiclass text problem—not a toy “accuracy contest.”

That’s why I wanted to measure, carefully, how well modern ML can map clinical text to syndrome labels.

---

## Slide 3 — Research question & motivation (~0:45) · words ≈ 110

Again, my exact question is on the slide: how accurately can ML classify TCM syndromes from symptoms and clinical data?

I’m not trying to replace a clinician. I’m asking an empirical question: given a **public** clinical benchmark, which modeling styles actually work—and where do they fail?

Three issues drove me. First, complex Chinese clinical narratives. Second, **148** syndrome classes with heavy imbalance. Third, a literature that mixes multi-label forests, CNNs on structured fields, and BERT-style models—often on **private** hospital data. I wanted one shared, reproducible setup where I could compare those ideas fairly against simple baselines.

---

## Slide 4 — Gong et al., 2023 (~0:55) · words ≈ 130

My first parent paper is **Gong and colleagues, 2023**, in *Frontiers in Genetics*. They study syndrome differentiation with a **multi-label** deep forest and biomedical text mining. Their point is that a patient may carry **more than one** syndrome at once, and that **feature selection**—including Pearson-style ranking—matters before you jump to a huge model.

That paper shaped how I think about **feature selection** and about being careful with label structure. But here’s the honest limit: the public dataset I use, **TCM-SD**, assigns **one** normalized syndrome per record. So my task is **single-label multiclass**, not multi-label. I did **not** reproduce their full multi-label deep forest. What I *did* adapt is the spirit of supervised feature ranking in a separate ablation experiment.

---

## Slide 5 — Huang et al., 2022 (~0:55) · words ≈ 125

The second paper is **Huang and colleagues, 2022**, in *JMIR Medical Informatics*. They build **Cross-FGCNN**—a CNN plus a cross-feature network—for dysmenorrhea syndromes using about sixty **structured four-examination fields**. Their key insight is that TCM features **interact**. If you treat every symptom as independent, you miss the clinical structure.

I learned from that: interactions matter, and four-exam structure is meaningful. In my project I implemented an **AdaptedCrossFGCNN** inspired by their idea. But I did **not** have their private Sichuan EMR table, so I adapted the idea onto free-text “virtual fields.” That’s an **adaptation**, not an exact replication—and I say that explicitly in the repo docs.

---

## Slide 6 — Chen et al., 2024 + connections (~0:55) · words ≈ 135

The third paper is **Chen and colleagues, 2024**, in *Integrative Medicine Research*. They push **deep learning for holistic syndrome differentiation**, including BERT-style encoding of clinical language plus CNN components.

What matters for me is the contrast: Gong emphasizes ranking and multi-label forests; Huang emphasizes structured crosses and CNNs; Chen emphasizes **language representation**. Together they motivated a single research design: take those *ideas*, place adapted versions on **one public multiclass benchmark**, and compare them against classical machine learning.

So now I’ll switch from literature to **my** implementation—dataset, methods, measured results, and what I claim as my contribution.

---

## Slide 7 — Dataset & preprocessing (~1:00) · words ≈ 140

For data I use **TCM-SD**, publicly linked from **github.com/Borororo/ZY-BERT**, under a non-commercial Creative Commons license, with the Ren et al. CCL 2022 paper as the dataset citation.

There are **54,152** clinical records and **148** `norm_syndrome` classes. Model inputs are free-text fields: chief complaint, description, and detection notes. The target is one syndrome label—multiclass.

I use a leakage-aware **70 / 10 / 20** split by patient ID and a clinical-text fingerprint, so the same patient story doesn’t leak across train, validation, and test. Features are train-only character TF-IDF plus simple length features, then SelectKBest with chi-square to five thousand features. Because labels are long-tailed, I care about **micro-F1 and macro-F1**, not just accuracy.

---

## Slide 8 — My ML methodology (~1:10) · words ≈ 145

Methodologically, I kept the pipeline simple and shared. Dataset → preprocess → features → train → validate → test once.

I first trained three classical baselines on the **same** matrices: Random Forest, Logistic Regression, and Linear SVM. Then I ran a feature-selection ablation—variance truncation versus mutual information, tree importance, and a Gong-inspired Pearson-style filter. Then I trained two deep adaptations: a Huang-inspired CNN and a Chen-inspired frozen Chinese BERT plus TextCNN.

The evaluation rule is strict: pick the best model using **validation micro-F1 only**, then score the held-out test set **once**. I do not tune on test. And the interactive teaching desk on my website is a **separate educational pattern demo**—it is **not** the trained TCM-SD classifier.

---

## Slide 9 — Results (~0:55) · words ≈ 130

Here are the measured validation results from my repository artifacts. **Linear SVM** led with about **0.752** accuracy and micro-F1, then Random Forest around **0.731**. Logistic Regression and both deep adaptations were lower—around **0.46 to 0.51** micro-F1.

Because SVM won on validation, I evaluated it on the locked test set of **10,777** examples. Test accuracy and micro-F1 were **0.7548**; macro-F1 was about **0.499**. So overall hit rate looks solid, but rare syndromes are still weak—that’s what macro-F1 tells us.

Feature selection did **not** uniformly help. And on this setup, the adapted deep models did **not** beat TF-IDF SVM or Random Forest. That doesn’t mean deep learning is “bad”—it means under my public-data adaptations and compute limits, simpler models won.

---

## Slide 10 — Contribution (~0:55) · words ≈ 130

So what did I actually contribute relative to the parent papers?

I did **not** invent a new architecture or claim state-of-the-art hospital performance. My contribution is a **reproducible shared-benchmark study**: classical ML and parent-paper–inspired adaptations, same splits, leakage checks, and a locked test. I also document clearly where I **deviate**—multiclass instead of Gong’s multi-label; adapted CNN/BERT instead of Huang’s and Chen’s original data heads.

The useful scientific takeaway for the research question is specific: on public TCM-SD clinical text, a Linear SVM reaches about **75.5%** test micro-F1 across 148 syndromes, while my adapted deep models lag, and rare classes remain hard. The website’s Research Results page shows those numbers; the Explorer is labeled as teaching-only.

---

## Slide 11 — Future work & close (~1:00) · words ≈ 125

Looking ahead, I want to improve **rare-class** performance and maybe add hierarchical TCM constraints. I’d also like richer Chinese clinical NLP, better calibration, and error-driven dictionary work on confused syndrome pairs. If a properly licensed **multi-label** corpus becomes available, I’d revisit Gong-style multi-label methods honestly instead of forcing them onto TCM-SD.

To close: my project asks how accurately ML can classify TCM syndromes from clinical text. On a public 148-class benchmark, classical margin models currently give the strongest verified answer in my repo—about three-quarters micro-F1—while adapted deep models underperform, and rare syndromes define the next frontier.

Thank you—I’m happy to take questions. The code and results are at **github.com/shiyx1224-shi/tcm-project**.

---

## Timing checklist

| Slides | Section | Target |
|--------|---------|-------:|
| 1–6 | Background + parent papers | 5:00 |
| 7–11 | Methods, results, contribution, future | 5:00 |
| **Total** | | **10:00** |

**Approx. total words above:** ~1,280 (comfortable 10-minute pace).
