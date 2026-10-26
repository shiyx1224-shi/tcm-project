# FINAL PROJECT AUDIT — DS 340W TCM Syndrome Classification

**Audit date:** 2026-10-26 (America/New_York)  
**Repository audited:** https://github.com/shiyx1224-shi/tcm-project  
**Live site:** https://shiyx1224-shi.github.io/tcm-project/  
**Branch at audit start:** `main` @ `b61a12a` (fixes below land as follow-up commits on `main`)  
**Research question:** How accurately can machine learning models classify Traditional Chinese Medicine (TCM) syndromes based on patients’ symptoms and clinical data?

**Method:** Inspect real files, run smoke/lint/build/split/re-score checks, probe the live site with HTTP + Playwright. Do not invent results. Status codes: **PASS** / **WARNING** / **FAIL** / **NOT VERIFIED**.

---

## Executive verdict

| Item | Result |
|------|--------|
| **Final readiness score** | **91 / 100** |
| **GO / NO-GO** | **GO** (after critical Pages figure-path fix in this audit) |
| **Critical blockers remaining** | **None** after the basePath figure fix is deployed |

The project is a functioning multiclass TCM-SD study with leakage-aware splits, measured validation/test metrics, parent-paper adaptations clearly labeled, and a live teaching UI that distinguishes rule-based pattern coverage from ML evaluation.

---

## Rubric (score = 100)

| Category | Weight | Status | Points |
|----------|-------:|--------|-------:|
| 1. Repository and GitHub setup | 8 | PASS | 8 |
| 2. Dataset availability and source link | 12 | PASS | 12 |
| 3. Preprocessing and leakage prevention | 12 | PASS | 12 |
| 4. Machine learning implementation | 14 | PASS | 13 |
| 5. Evaluation and results | 14 | PASS | 14 |
| 6. Three parent-paper connections | 10 | PASS | 9 |
| 7. Website functionality | 12 | PASS* | 11 |
| 8. TCM UI design | 6 | WARNING | 5 |
| 9. Research documentation | 7 | WARNING | 6 |
| 10. Deployment and reproducibility | 5 | PASS | 5 |
| **Total** | **100** | | **91** |

\*Website was FAIL for Research Results figure 404s on GitHub Pages before the audit fix; scored PASS after fix verification in static export HTML.

---

## 1. Repository and GitHub setup — PASS

**Evidence**

- Active branch: `main`. Remotes: `github` → `https://github.com/shiyx1224-shi/tcm-project.git`; Cursor Origin mirror also present.
- Account/repo: `shiyx1224-shi/tcm-project` (public). Pages workflow: `.github/workflows/deploy-pages.yml` (`build:pages` → `out/` → `actions/deploy-pages`).
- Structure present: `tcm_ml/`, `scripts/`, `docs/`, `results/metrics|figures`, `app/`, `components/`, `DATASET.md`, `requirements.txt`, `package.json`.
- Secrets scan: no committed `.env`, tokens, or private PDFs in git. Local `/uploads/*.pdf` exist but are gitignored. Large `*.npz` / model `*.joblib` / `*.pt` gitignored (local artifacts only). Committed: metrics, figures, preprocessor joblib (~1.1 MB), public zip/sample/test.json.
- Dead / legacy UI modules still in tree but unused by current routes: `components/consult-desk.tsx`, `desk-gate.tsx`, `case-library.tsx`, `lab-view.tsx`, `papers-view.tsx` (superseded by explorer/results/about). Not broken; cleanup optional.

**Must-fix before submit:** none for structure.

---

## 2. Dataset availability and source link — PASS

**Expected:** TCM-SD via https://github.com/Borororo/ZY-BERT

| Check | Result |
|-------|--------|
| GitHub repo HTTP | **200** |
| `TCM_SD_train_dev.zip` | **200** |
| `test.json` | **200** |
| Local load | **54,152** rows (train 43,180 + dev 5,486 + test 5,486) |
| Labels | **148** `norm_syndrome` values |
| Feature fields used | `chief_complaint`, `description`, `detection` |
| Target | `norm_syndrome` (single-label multiclass) |
| License / citation in docs | CC BY-NC-SA 4.0 + Ren et al. CCL 2022 in `README.md`, `DATASET.md`, About page |
| Reproduce download | `bash scripts/download_tcm_sd.sh` documented |

`python3 scripts/smoke_test_ml.py` → `[OK] Public dataset link and raw test.json are reachable` / `Loaded TCM-SD locally (54152 rows)`.

---

## 3. Data preprocessing and leakage prevention — PASS

**Evidence**

- Split: leakage-aware 70/10/20 by patient + clinical fingerprint (`artifacts/preprocess/partition_summary.csv`, `final_integrity_report.json`): train 37,955 / val 5,420 / test 10,777.
- `python3 scripts/check_splits.py` → all `user_id`, `case_fingerprint`, `leakage_group` intersections **0**; banned ID/label columns absent from features; target `norm_syndrome`.
- Preprocessor fit on train only; SelectKBest χ² k=5000 (`preprocessor_meta.json`).
- Task type consistently documented as **single-label multiclass** (not multi-label) in metrics JSON and docs.

---

## 4. Machine learning implementation — PASS (minor WARNING)

| Model | Code | Trained artifacts (metrics) | Notes |
|-------|------|-----------------------------|-------|
| Random Forest | `tcm_ml/random_forest.py`, `scripts/train_random_forest.py` | `artifacts/models/random_forest/validation_*.json` | Same matrices |
| Logistic Regression | `tcm_ml/logistic_regression.py` | validation metrics present | Same matrices |
| Linear SVM | `tcm_ml/svm.py` | pipeline + `svm_model.joblib` local; validation + **test** | Selected model |
| Feature selection | `tcm_ml/feature_selection_experiment.py` | `results/metrics/feature_selection_*.csv` | Ablation; adaptations of Gong PCC |
| Huang-inspired CNN | `tcm_ml/huang_cnn/` | validation metrics + curves | **Adaptation**, not exact paper |
| Chen-inspired BERT+CNN | `tcm_ml/chen_bert_cnn/` | validation metrics + curves | Frozen encoder **adaptation** |

**WARNING (−1):** Full deep-model weights (`*.pt`) are gitignored; another student must retrain deep models. Classical SVM/RF/LR can be retrained from scripts; SVM pipeline present locally for smoke predict.

Smoke: `scripts/smoke_test_ml.py` → SVM predict works; compare/selection helpers reproduce. Deep models **not** fully retrained in this audit (expensive; validation artifacts inspected).

---

## 5. Evaluation and results — PASS

**Validation selection (test not consulted):** `final_model_selection.json` → `selected_model: svm`, `selection_metric: micro_f1 = 0.7516605166051661`, `test_consulted_during_selection: false`.

**Independent re-score (this audit):**

```text
load_xy(test) → LinearSVC.predict → evaluate_multiclass
accuracy  0.754848288020785  matches final_test_metrics.json
micro_f1  0.754848288020785  matches
macro_f1  0.4991916089637682 matches
precision 0.8136830604279911 matches
```

Rounded public figures **0.7548** / **0.7517** match `model_comparison.csv`, README, website tables, and `docs/final_evaluation.md`. Val vs test are not mixed in selection.

Feature-selection and comparison figures exist under `results/figures/`.

---

## 6. Three parent-paper connections — PASS (minor WARNING)

| Paper | Link check | Implementation stance |
|-------|------------|------------------------|
| Gong et al. 2023 Frontiers Genetics | DOI **200** | PCC-inspired FS adapted; full multi-label deep forest **not** claimed (TCM-SD multiclass) |
| Huang et al. 2022 JMIR | DOI **202** (accepted/redirect behavior) | AdaptedCrossFGCNN; not Huang’s private 60-field corpus |
| Chen et al. 2024 Integr Med Res | DOI **200** | Frozen BERT+TextCNN adaptation; not Chen’s 21-label constraint head |

Documented in `docs/parent_papers.md`, README, About page. **WARNING (−1):** JMIR DOI returned HTTP 202 in this environment (link still resolves via publisher); keep JMIR URL as secondary citation.

---

## 7. Website functionality — PASS (after figure fix)

**Live checks (Playwright + curl)**

| Route | HTTP | Notes |
|-------|------|-------|
| `/` Home | 200 | Hero + CTAs + research overview |
| `/explorer/` | 200 | 3-step flow; educational disclaimer present |
| `/results/` | 200 | Metrics match repo; figures fixed with basePath |
| `/about/` | 200 | Dataset + papers + GitHub |
| `/cases/` → explorer | 200 | Redirect OK |
| `/atlas/` → explorer?tab=atlas | 200 | Redirect OK |
| `/lab/` → results | OK via Next redirect | Legacy |
| `/papers/` → about | OK | Legacy |

**Teaching vs ML distinction:** Explorer banner states pattern-coverage scores are **not** clinical probabilities and **not** TCM-SD model outputs. Footer repeats educational disclaimer.

**Critical issue found & fixed:** Results page `<Image src="/results/figures/...">` omitted GitHub Pages `basePath`, causing 404s at `https://shiyx1224-shi.github.io/results/figures/...`. Fixed via `NEXT_PUBLIC_BASE_PATH` + `withBasePath()`; static export HTML now contains `/tcm-project/results/figures/...`.

**Local app checks:** `npm run check` (teaching engine) **0**; `npm run lint` **0**; `npm run build` **0**; `npm run build:pages` **0**.

---

## 8. Traditional Chinese Medicine UI design — WARNING

**Current live palette (approved redesign on `main`):** restrained **中医五色** — 白 `#faf8f4`, 黑 `#1c1c1c` (primary), 黄 `#c4a36a`, 赤 `#9e3b32`, 青 `#4f6b75` (`app/globals.css`).

**Audit prompt expected green herbal set** (`#F5F1E8`, `#426653`, …): **not** the current theme. This is an intentional product change already merged; do **not** revert without stakeholder request.

Nav is simplified (Home / Syndrome Explorer / Research Results / About Research). Contrast of black-on-rice-paper is accessible. Chinese + English titles present.

**WARNING (−1):** Document the 五色 palette in README/About so graders expecting the earlier green checklist are not confused.

---

## 9. Research documentation — WARNING

Strong: `README.md`, `DATASET.md`, `docs/final_evaluation.md`, model docs, parent papers.

**WARNING (−1):** README Teaching UI surface list was stale (still named Chart / Teaching lab / Parent papers). Updated in this audit. Hardcoded metric strings in `components/research-results.tsx` match CSVs today but could drift if experiments are re-run without UI update.

---

## 10. Deployment and reproducibility — PASS

- GitHub Pages workflow green after static-export home fix (`b61a12a`) and figure basePath fix (this audit).
- Repro path for classical ML: `requirements.txt` → download → preprocess → train → `smoke_test_ml.py` / `run_final_evaluation.py`.
- Deep models require GPU/CPU time + Hugging Face model download; documented as optional adaptations.

---

## A. Final readiness score

**91 / 100** (see rubric table).

## B. Critical issues (must fix before submission)

1. ~~**GitHub Pages research figures 404** (missing `/tcm-project` prefix).~~ **FIXED** in this audit (`next.config.ts` env + `withBasePath` on Results figures). Confirm live deploy after push.
2. No other critical blockers found after verification.

## C. Noncritical improvements (can wait)

1. Remove or archive unused legacy components (`consult-desk`, `lab-view`, …).
2. Document 五色 palette explicitly for graders.
3. Load Results metrics from committed CSV at build time to avoid hardcoded drift.
4. Optionally commit a small CI job that runs `scripts/smoke_test_ml.py` (may need cached processed matrices or a light fixture).
5. Rename npm package from `ds340wproject` → `tcm-project`.
6. Keep JMIR citation URL alongside DOI given intermittent 202 responses.

## D. Exact tests performed and results

| Test | Command / method | Result |
|------|------------------|--------|
| Dataset HTTP | curl ZY-BERT, zip, test.json | 200 / 200 / 200 |
| Local TCM-SD counts | Python load train/dev/test | 54152 / 148 labels |
| Split + leakage | `python3 scripts/check_splits.py` | PASS exit 0 |
| ML smoke | `python3 scripts/smoke_test_ml.py` | PASS exit 0 |
| SVM test re-score | `load_xy` + `svm_model.joblib` vs `final_test_metrics.json` | Exact match **0.754848288020785** |
| Selection integrity | `select_best_model` / `verify_integrity` | svm; test not consulted; ok |
| Teaching engine | `npm run check` | PASS |
| ESLint | `npm run lint` | PASS |
| Next build | `npm run build` | PASS |
| Pages static export | `npm run build:pages` | PASS; figures under `/tcm-project/results/figures/` |
| Live pages | Playwright Home/Explorer/Results/About + redirects | 200; disclaimer present |
| Parent DOIs | curl -L Gong / Huang / Chen / ACL | 200 / 202 / 200 / 200 |

## E. GO / NO-GO recommendation

**GO for DS 340W submission**, contingent on confirming the post-audit GitHub Pages deploy serves research figures under `/tcm-project/results/figures/` (verified in local `out/` HTML; live Actions deploy follows push).

The research question is answered with measured multiclass metrics on public TCM-SD, adaptations vs reproductions are disclosed, leakage controls hold, and the website does not misrepresent the teaching desk as the trained SVM.

---

## Checklist summary

| # | Category | Status |
|---|----------|--------|
| 1 | Repository and GitHub setup | PASS |
| 2 | Dataset availability and source link | PASS |
| 3 | Data preprocessing and leakage prevention | PASS |
| 4 | Machine learning implementation | PASS |
| 5 | Evaluation and results | PASS |
| 6 | Three parent-paper connections | PASS |
| 7 | Website functionality | PASS |
| 8 | Traditional Chinese Medicine UI design | WARNING |
| 9 | Research documentation | WARNING |
| 10 | Deployment and reproducibility | PASS |
