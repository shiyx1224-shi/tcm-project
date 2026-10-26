# Parent paper notes (DS340W)

Source PDFs were used for course design only and are **not** committed (copyright). Cite the DOIs below.

## 1. Multi-label deep forest (Gong et al., 2023)

- **Problem:** One disease can carry several syndromes; TCM corpora are small and synonym-heavy.
- **Method:** Symptom name standardization → Pearson-adjusted multi-label Relief feature selection (PCC-MLRF) → multi-label deep forest (ML-PRDF).
- **Evaluation:** Multi-label criteria (Hamming loss, one-error, coverage, ranking loss, average precision), not single-label accuracy alone.
- **Desk mapping:** Multi-label ranking, synonym dictionary, teaching-lab set metrics, Relief-style feature leaders.

## 2. Cross-feature CNN (Huang et al., 2022)

- **Problem:** Charts are sparse and high-dimensional; flat symptom vectors hide which signs sit in the same diagnostic field.
- **Method:** Structure cases by the four examinations; embed fields; learn linear and convolutional crosses; classify dysmenorrhea syndromes.
- **Data context:** Thousands of real dysmenorrhea cases after structuring into diagnostic fields (paper reports strong accuracy on that curated corpus — not claimed here).
- **Desk mapping:** Examination-grouped intake, missing tongue/pulse discount, named cross-feature boosts, dysmenorrhea lens.

## 3. Holistic TCM-BERT-CNN (Chen et al., 2024)

- **Problem:** Most models stay inside one disease; holistic differentiation needs principles, organs, and pathologies that can co-exist under TCM constraints.
- **Method:** BERT + CNN with classification constraints from holistic syndrome differentiation; symptom→syndrome text task; constraint pairs such as exterior vs interior and deficiency vs excess.
- **Desk mapping:** Holistic lens, competing-pair damping, atlas co-occurrence of key signs.
