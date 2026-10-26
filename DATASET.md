# Dataset selection (DS 340W)

**Research question:** How accurately can machine learning models classify TCM syndromes based on patients’ symptoms and clinical data?

**Selected dataset:** **TCM-SD** (Traditional Chinese Medicine — Syndrome Differentiation benchmark)

**Professor-facing public link (use this):**  
**https://github.com/Borororo/ZY-BERT**

Mirror / catalog page (Aliyun Tianchi):  
https://tianchi.aliyun.com/dataset/139034  
(also referenced from the GitHub README as `dataId=139034`)

Local copy (downloaded for this project): `data/raw/TCM-SD/`

Install ML deps with `pip install -r requirements.txt`, then `bash scripts/download_tcm_sd.sh`.

This document records verified accessibility, schema, license, and why alternatives were not chosen. **No models are trained here.**

---

## Recommendation summary

| Candidate | Verdict |
|-----------|---------|
| **TCM-SD via [Borororo/ZY-BERT](https://github.com/Borororo/ZY-BERT)** | **Selected.** Public link works; 54,152 real clinical records; free-text symptoms + four-exam notes + syndrome labels; documented CC BY-NC-SA 4.0; peer-reviewed citation. |
| [web333panda/TCM-Dataset](https://github.com/web333panda/TCM-Dataset) (Gong et al. parent paper) | **Not selected as primary.** Public repo exists, but **no LICENSE**; kidney spreadsheet is mostly literature metadata (many empty syndrome cells); stomach file is usable multi-label-ish symptom text but smaller and license-unclear. Keep as optional secondary only if license is clarified. |
| Huang et al. 2022 dysmenorrhea set | **Not publicly downloadable** (Sichuan TCM platform + Chinese literature; no open dump in the paper). |
| Chen et al. 2024 holistic set | **Not a public dump** (“available within the article and from the corresponding author upon reasonable request”). |

---

## 1. Selected: TCM-SD (ZY-BERT repository)

### Exact public links

| Role | URL |
|------|-----|
| **Canonical project + data page** | https://github.com/Borororo/ZY-BERT |
| Train + dev zip (direct) | https://raw.githubusercontent.com/Borororo/ZY-BERT/main/TCM_SD_train_dev.zip |
| Test JSON (direct) | https://raw.githubusercontent.com/Borororo/ZY-BERT/main/test.json |
| Sample zip | https://raw.githubusercontent.com/Borororo/ZY-BERT/main/TCM%20Data%20Sample.zip |
| Tianchi catalog | https://tianchi.aliyun.com/dataset/139034 |
| Paper (ACL Anthology) | https://aclanthology.org/2022.ccl-1.80/ |
| arXiv | https://arxiv.org/abs/2203.10839 |

### Citation

Ren M, Huang H, Zhou Y, Cao Q, Bu Y, Gao Y. TCM-SD: A Benchmark for Probing Syndrome Differentiation via Natural Language Processing. In: *Proceedings of the 21st Chinese National Conference on Computational Linguistics (CCL 2022)*. 2022:908–920. https://aclanthology.org/2022.ccl-1.80/

```bibtex
@inproceedings{mucheng-etal-2022-tcm,
  title = {{TCM}-{SD}: A Benchmark for Probing Syndrome Differentiation via Natural Language Processing},
  author = {Ren, Mucheng and Huang, Heyan and Zhou, Yuxiang and Cao, Qianwen and Bu, Yuan and Gao, Yang},
  booktitle = {Proceedings of the 21st Chinese National Conference on Computational Linguistics},
  year = {2022},
  address = {Nanchang, China},
  publisher = {Chinese Information Processing Society of China},
  url = {https://aclanthology.org/2022.ccl-1.80},
  pages = {908--920}
}
```

### License and research-use restrictions

| Layer | License | Notes |
|-------|---------|-------|
| **Dataset** (per upstream README) | **[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)** | Attribution required; **non-commercial** use; share-alike if you redistribute adapted data. Course research / academic homework fits NC if not sold commercially. |
| Repository software (`LICENSE` file) | MIT | Applies to code packaging; **do not confuse with the dataset license**. |

**Restrictions to respect:** do not use for commercial products; keep attribution; if you redistribute a modified dataset, keep CC BY-NC-SA 4.0 (or compatible SA terms). Clinical text may still contain sensitive narrative—store responsibly; do not re-identify patients.

### Download accessibility (verified)

- GitHub repository is **public** (HTTP 200).
- `TCM_SD_train_dev.zip` and `test.json` download without login via raw.githubusercontent.com (verified in this environment).
- Re-download script: `scripts/download_tcm_sd.sh`

### Record counts (verified after download)

| Split | Records |
|-------|--------:|
| `train.json` | 43,180 |
| `dev.json` | 5,486 |
| `test.json` | 5,486 |
| **Total** | **54,152** |

- **Syndrome classes (`norm_syndrome` / `syndrome_vocab.txt`):** **148**
- Paper description: real-world Chinese clinical notes; long-tail label distribution.

### Feature columns and target labels

Each JSON line / object includes:

| Field | Role |
|-------|------|
| `user_id` | Record identifier |
| `lcd_id` | Disease / ICD-style code used in the release |
| `lcd_name` | Disease name (clinical context) |
| `chief_complaint` | Chief complaint (symptom-focused short text) |
| `description` | Admission / history narrative (clinical symptom information) |
| `detection` | Four diagnostic methods record (inspection, listening/smelling, inquiry, palpation-style template text) |
| `syndrome` | Syndrome string |
| `norm_syndrome` | **Normalized target syndrome label** (use this as the primary target) |

**Input for classification:** typically concatenate or jointly encode `chief_complaint` + `description` + `detection` (patient symptoms / clinical information in free text).  
**Target:** `norm_syndrome` (one of 148 classes).

### Single-label vs multi-label

- **Primary task in TCM-SD / ZY-BERT:** **single-label multiclass** syndrome differentiation (one `norm_syndrome` per record).
- This still matches the research question (symptoms/clinical text → syndrome class) and is the standard public SD benchmark.
- Parent papers Gong (multi-label) and Chen (holistic multi-output) use **different** label schemes; those exact corpora are not open or not license-clear. TCM-SD is the strongest **public** fit for accuracy evaluation today.

### Original publication

- CCL 2022 paper above; clinical notes described as real-world records (with quality control / syndrome normalization in the paper).
- Related model release: ZY-BERT (domain PLM); **not required** to use the dataset for classical ML baselines.

### Local paths after download

```
data/raw/TCM-SD/
  TCM_SD_train_dev.zip      # committed; contains train.json + dev.json
  test.json                 # committed (not inside the zip)
  syndrome_vocab.txt
  syndrome_knowledge.json
  TCM_Data_Sample.zip
  TCM Data Sample/
  UPSTREAM_README.md
  UPSTREAM_LICENSE_MIT_SOFTWARE.txt
  SHA256SUMS.txt
  train.json / dev.json     # extracted locally; gitignored (unzip the zip)
```

### Download instructions

```bash
# From the project root
bash scripts/download_tcm_sd.sh
```

Or manually:

```bash
mkdir -p data/raw/TCM-SD && cd data/raw/TCM-SD
curl -fsSL -o TCM_SD_train_dev.zip \
  https://raw.githubusercontent.com/Borororo/ZY-BERT/main/TCM_SD_train_dev.zip
curl -fsSL -o test.json \
  https://raw.githubusercontent.com/Borororo/ZY-BERT/main/test.json
unzip -qo TCM_SD_train_dev.zip
```

---

## 2. Investigated: web333panda/TCM-Dataset (Gong et al. link)

**Public link:** https://github.com/web333panda/TCM-Dataset  
**Parent paper:** Gong et al., *Frontiers in Genetics*, 2023 (multi-label deep forest).  
**Accessibility:** Public GitHub; files downloadable without login.  
**License:** **None declared** on the repository (API returns no license) — **unsuitable as the sole graded dataset** until rights are clarified.

### Contents found

| File | Approx. rows | Notes |
|------|-------------:|-------|
| `肾衰数据(1).xls` (kidney / CRF-related) | 2,283 | Columns are largely literature / abstract metadata (`LCYJMC`, `YJFF`, …). `ZHMC` (syndrome) filled in ~1,187 rows; `ZZMC` (symptom string, `$`-separated) filled in ~905 rows. **Not** the clean 645×755 multi-label matrix described in Gong Table 1. |
| `胃部疾病数据.xlsx` (stomach) | 1,525 | Columns: `ID`, `症候` (syndrome), `症状` (symptoms), `编号`. Same symptom text can map to multiple syndromes via `编号` (≈2.9 syndromes/group) → **multi-label-friendly**, but smaller and **unlicensed**. |

**Why not primary:** missing license; kidney table is not a ready patient-feature matrix matching the paper’s reported schema; weaker “working public dataset for the course” posture than TCM-SD.

---

## 3. Parent-paper datasets (status)

| Paper | Dataset claimed | Public working link? |
|-------|-----------------|----------------------|
| Huang et al. 2022 | 5,273 dysmenorrhea EMRs (Sichuan platform + literature) | **No** open dump |
| Gong et al. 2023 | Kidney + stomach multi-label | GitHub above — **partial / license-unclear** |
| Chen et al. 2024 | 6,148 guideline/textbook samples | **On request**, not a stable public URL |

---

## 4. How TCM-SD serves the research question

| Requirement | TCM-SD |
|-------------|--------|
| Actual patient symptoms / clinical information | Yes — `chief_complaint`, `description`, `detection` |
| Corresponding TCM syndrome labels | Yes — `norm_syndrome` (148 classes) |
| Working public link | Yes — https://github.com/Borororo/ZY-BERT |
| Size adequate for ML accuracy study | Yes — 54,152 records |
| Documented license for research | Yes — CC BY-NC-SA 4.0 |

**Planned evaluation framing (for later modeling, not done yet):** multiclass accuracy / macro-F1 / per-class metrics on the official train/dev/test splits; optionally compare text-only vs four-exam (`detection`) ablation. Multi-label extensions remain future work if a licensed multi-label corpus becomes available.
