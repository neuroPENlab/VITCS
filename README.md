# VITCS: Visually Induced Threat Conditioning Signature

Analysis code accompanying the manuscript *A generalizable brain signature of human threat learning*

This repository contains the MATLAB and Python code used to train, validate, and characterize **VITCS**, a whole-brain SVM-based predictive signature of threat conditioning, and to reproduce the analyses reported in the main text and Supplementary Information.

---

## Contents

```
.
├── data/
│   ├── brainmask.nii
│   ├── training_data.mat
│   ├── test_data.mat
│   ├── 10fold_CV_VITCS.mat
│   ├── 10fold_CV_VITCS-early.mat
│   └── 10fold_CV_VITCS-late.mat
│
├── scripts/
│   ├── barplot_columns_modified_MODIFICATION.md (barplot_columns_modified.m itself is NOT included - see below)
│   │
│   ├── s01_train_test_split.m
│   ├── s02_train_VITCS_signature.m
│   ├── s03_1_validation_VITCS_test_set.m
│   ├── s03_2_full_sample_xval_pattern_expression.m
│   ├── s04_1_generalization_ENIGMA.m
│   ├── s04_2_generalization_ENIGMA_analysis.py
│   ├── s05_VITCS_bootstrap_feature_stability.m
│   ├── s06_VITCS_specificity.m
│   ├── s07_mediation_analysis.m
│   ├── s08_anxiety_risk_analysis.py
│   ├── s09_comparison_existing_signatures.m
│   ├── s10_1_VITCSearly_signature.m
│   ├── s10_2_VITCSlate_signature.m
│   │
│   ├── fig02a_1_reliable_anatomy_VITCS_PREPROC.sh
│   ├── fig02a_2_reliable_anatomy_VITCS_mricrogl.py
│   ├── fig02b_test_set_roc_plot.m
│   ├── fig02c_test_set_barplot.m
│   ├── fig04_existing_signatures_accuracy.m
│   ├── figsup03_neurosynth_wordcloud.py
│   ├── figsup05_VITCS_vs_univariate_mricrogl.py
│   ├── figsup06a_1_reliable_anatomy_VITCS_early_PREPROC.sh
│   ├── figsup06a_2_reliable_anatomy_VITCS_early_mricrogl.py
│   ├── figsup06d_1_reliable_anatomy_VITCS_late_PREPROC.sh
│   └── figsup06d_2_reliable_anatomy_VITCS_late_mricrogl.py
│
├── utils/
│   ├── run_signature_training.m
│   ├── run_test_set_validation.m
│   ├── run_full_sample_xval_pattern_expression.m
│   ├── run_bootstrap_feature_stability.m
│   ├── process_reliable_anatomy.sh
│   └── cluster_prunning.sh
│
└── figures/                  (output only - populated by running the fig_*/figsup_* scripts above; empty in this repository)
```

Scripts prefixed `sNN_` are the main analysis pipeline, run in numerical order. Scripts prefixed `fig`/`figsup` reproduce the figure panels and can be run in any order, after the corresponding `sNN_` analysis; they write their output images to `figures/`. Scripts prefixed `run_` (in `utils/`) are shared subroutines called by more than one `sNN_` script (e.g. the same training/validation/bootstrap routine is reused for the main VITCS model and for the VITCS-early / VITCS-late variants).

All code lives under `scripts/`; `figures/` and `results/` hold only what the code *generates* - nothing under either folder needs to be tracked as source.

`data/` contains the fixed inputs the pipeline reads as a starting point (brain mask, Training/Test split, 10-fold CV assignments) - as opposed to `results/`, which holds everything the scripts *generate*. See "Notes on reproducibility" below for what's included here and why.

**A note on `barplot_columns_modified.m`:** `fig02c_test_set_barplot.m` depends on a locally modified copy of CANlab's `barplot_columns.m`, meant to live alongside the original inside your CANlab Core Tools installation. To avoid redistributing a derivative of third-party licensed code, this
modified file is **not included** here. `scripts/barplot_columns_modified_MODIFICATION.md` gives exact, step-by-step instructions so you can recreate it yourself before running `fig02c_test_set_barplot.m`.

---

## Requirements

**MATLAB** (developed and tested on R2024a, macOS)
- Statistics and Machine Learning Toolbox
- [CANlab Core Tools](https://github.com/canlab/CanlabCore) (`fmri_data`, `predict`, `roc_plot`, `canlab_pattern_similarity`, `threshold`, `write`,
  `resample_space`, `load_image_set`, `correlation`)
- [CANlab Mediation Toolbox](https://github.com/canlab/MediationToolbox) (`mediation.m`)
- Spider Toolbox (SVM backend used by CANlab's `predict`)

**Python** (developed with Python 3.13.9, macOS)
- `pandas`, `numpy`, `scipy`, `scikit-learn`, `pingouin`, `matplotlib`, `seaborn`, `wordcloud`

**Other tools** (figure generation only)
- [FSL 6.0.7.18](https://fsl.fmrib.ox.ac.uk/) (`fslmaths`, `fslstats`, `cluster`) for `fig_1_process_reliable_anatomy.sh` and `fig_2_cluster_prunning.sh`
- [MRIcroGL 15.7.4](https://www.nitrc.org/projects/mricrogl) for the `*_mricrogl.py` brain-rendering scripts

**Hardware**
No non-standard hardware is required; all analyses were run on a standard desktop/laptop computer (no GPU needed).

---

## Installation

1. **Clone this repository.**
   ```bash
   git clone https://github.com/neuroPENlab/VITCS.git
   cd VITCS
   ```

2. **Set up MATLAB dependencies.** Install the following and add them to your MATLAB path (`addpath(genpath(...))`), in addition to this repository's own `utils/` folder (already added at the top of each `sNN_` script):
   - [CANlab Core Tools](https://github.com/canlab/CanlabCore)
   - [CANlab Mediation Toolbox](https://github.com/canlab/MediationToolbox)
   - Spider Toolbox
   
   No `mex`/compilation step is required for any of the above; adding them to the path is sufficient.

3. **Set up the Python environment.** A `requirements.txt` is provided:
   ```bash
   python3 -m venv vitcs_env
   source vitcs_env/bin/activate      # Windows: vitcs_env\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Optional, figure-generation only:** install [FSL](https://fsl.fmrib.ox.ac.uk/fsl/docs/#/install/index) and [MRIcroGL](https://www.nitrc.org/projects/mricrogl) following their own installation instructions. These are only needed for the `fig_*`/`figsup_*` scripts, not for the main `sNN_` analysis pipeline.

5. **Edit the path placeholders.** Every script has one or more `<PATH_TO_...>` variables near the top, marked `% <-- EDIT THIS` (MATLAB) or `# <-- EDIT THIS` (Python). These must point to your local copies of the data described below before running anything (see "Data").

**Typical install time:** ~15–20 minutes on a standard desktop/laptop, excluding the time to install the third-party toolboxes/tools in steps 2 and 4 (which depend on whether they are already available on your system).

---

## Data

Raw imaging data and individual-level questionnaire data are **not included** in this repository. All scripts expect a `<PATH_TO_...>` placeholder (marked `% <-- EDIT THIS` / `# <-- EDIT THIS`) to be filled in with local paths before running, pointing to:

- first-level contrast images (CS+/CS-, newCS+/newCS-, early/late variants), organized as `<contrastdir>/<subject>/REVERSAL/FIRST_LEVEL_REVERSAL_Half_ALL/`
- questionnaire data (STAI-T, SPSRQ-P) per participant
- skin conductance response (SCR) and subjective rating tables
- restricted ENIGMA-Anxiety FC Group participant-level data (multi-site consortium data, not publicly shareable)
- Monetary Incentive Delay (MID) task contrast images (N=39; `s06_VITCS_specificity.m`) - restricted, not publicly shareable
- precomputed HCP-YA VITCS pattern-expression scores (`s06_VITCS_specificity.m`), provided by the HCP-YA collaborators (T. Wager)
- comparison signature weight maps (Liu-SUITAS, Wen-BeyondThreat, Wager-NPS) not bundled with CANlab

**External inputs not generated by any script in this repository:**
- Neurosynth anatomical/functional term decoding (`figsup03_neurosynth_wordcloud.py`) - produced manually via [neurosynth.org](https://neurosynth.org); see Supplementary Text, "Extraction of anatomical and functional terms using NeuroSynth"
- univariate contrast maps used for comparison in `figsup05_VITCS_vs_univariate_mricrogl.py` - downloaded from a previously published study (DOI: *10.1038/s41467-025-63078-x*)

To reproduce the published Training/Test split without access to the raw data, `data/training_data.mat` and `data/test_data.mat` (the exact partition used in the manuscript, `n = 138` / `n = 34`) are provided in this repository — see `s01_train_test_split.m`, `USE_PUBLISHED_SPLIT`.

---

## Pipeline overview

Run in this order (after editing the path placeholders in each script):

| Step | Script | What it does |
|---|---|---|
| 1 | `s01_train_test_split.m` | Stratified 80/20 Training/Test split (by STAI-T) |
| 2 | `s02_train_VITCS_signature.m` | Train VITCS with 10-fold CV; SVM-C sensitivity analysis |
| 3 | `s03_1_validation_VITCS_test_set.m` | Validate VITCS on the held-out Test Set (acquisition + reversal) |
| 4 | `s03_2_full_sample_xval_pattern_expression.m` | Out-of-fold pattern expression, full sample (N=172) |
| 5 | `s04_1_generalization_ENIGMA.m` + `s04_2_generalization_ENIGMA_analysis.py`| Pattern expression & accuracy across the 26 ENIGMA-Anxiety FC datasets |
| 6 | `s05_VITCS_bootstrap_feature_stability.m` | Bootstrap (5,000 resamples) + FDR-thresholded weight map |
| 7 | `s06_VITCS_specificity.m` | Specificity vs. reward processing (MID task, HCP-YA) |
| 8 | `s07_mediation_analysis.m` | SCR mediation of VITCS → subjective arousal/valence |
| 9 | `s08_anxiety_risk_analysis.py` | VITCS expression, high- vs low-anxiety-risk tertiles |
| 10 | `s09_comparison_existing_signatures.m` | Benchmark vs. published signatures + shared variance |
| 11 | `s10_1_VITCSearly_signature.m` / `s10_2_VITCSlate_signature.m` | Train/validate the stage-specific early/late variants |

### Re-running the signature-parametrized scripts

Four scripts — `s04_1_generalization_ENIGMA.m`, `s04_2_generalization_ENIGMA_analysis.py`, `s07_mediation_analysis.m`, and `s08_anxiety_risk_analysis.py` — take a `SIGNATURE` variable at the top of the script and must be **re-run once per signature/model** below to reproduce every number reported in the manuscript. Each block must be run after its corresponding prerequisite step in the table above.

**VITCS (main model)** — prerequisite: Step 2 (`s02_train_VITCS_signature.m` and `s03_2_full_sample_xval_pattern_expression.m`)

| Script | `SIGNATURE` value |
|---|---|
| `s04_1_generalization_ENIGMA.m` | `'VITCS'` |
| `s04_2_generalization_ENIGMA_analysis.py` | `'VITCS'` |
| `s07_mediation_analysis.m` | `'VITCS'` |
| `s08_anxiety_risk_analysis.py` | `'VITCS'` |

**Comparison signatures** — prerequisite: Step 10 (`s09_comparison_existing_signatures.m`)

| Script | `SIGNATURE` value |
|---|---|
| `s04_1_generalization_ENIGMA.m` | `'Reddan-Threat'` and `'Liu-SUITAS'` |
| `s04_2_generalization_ENIGMA_analysis.py` | `'Reddan-Threat'` and `'Liu-SUITAS'` |
| `s07_mediation_analysis.m` | `'Reddan-Threat'` and `'Liu-SUITAS'` |
| `s08_anxiety_risk_analysis.py` | `'Reddan-Threat'` and `'Liu-SUITAS'` |

**VITCS-early** — prerequisite: `s10_1_VITCSearly_signature.m`

| Script | `SIGNATURE` value |
|---|---|
| `s04_1_generalization_ENIGMA.m` | `'VITCS_early'` |
| `s04_2_generalization_ENIGMA_analysis.py` | `'VITCS_early'` |
| `s07_mediation_analysis.m` | `'VITCS_early'` |
| `s08_anxiety_risk_analysis.py` | `'VITCS_early'` |

**VITCS-late** — prerequisite: `s10_2_VITCSlate_signature.m`

| Script | `SIGNATURE` value |
|---|---|
| `s04_1_generalization_ENIGMA.m` | `'VITCS_late'` |
| `s04_2_generalization_ENIGMA_analysis.py` | `'VITCS_late'` |
| `s07_mediation_analysis.m` | `'VITCS_late'` |
| `s08_anxiety_risk_analysis.py` | `'VITCS_late'` |


### Figures

All figure scripts below live in `scripts/` alongside the analysis pipeline (see "Contents"); they write their output images to `figures/`.

| Script | Figure |
|---|---|
| `fig_1_process_reliable_anatomy.sh`, `fig_2_cluster_prunning.sh` | FSL preprocessing (cluster separation, binarization, pruning) of the bootstrap-thresholded weight maps from step 6, before rendering |
| `fig02a_1_reliable_anatomy_VITCS_PREPROC.sh`, `fig02a_2_reliable_anatomy_VITCS_mricrogl.py` | Fig. 2a — VITCS reliable-anatomy brain map |
| `fig02b_test_set_roc_plot.m` | Fig. 2b — Test Set ROC curves (CV / acquisition / reversal) |
| `fig02c_test_set_barplot.m` | Fig. 2c — Test Set pattern expression, CS+ vs. CS- |
| `fig04_existing_signatures_accuracy.m` | Fig. 4 — accuracy comparison across signatures |
| `figsup03_neurosynth_wordcloud.py` | Supp. Fig. 3 — Neurosynth decoding word clouds |
| `figsup05_VITCS_vs_univariate_mricrogl.py` | Supp. Fig. 5 — VITCS vs. univariate contrast overlay |
| `figsup06a_1_..._VITCS_early_PREPROC.sh`, `figsup06a_2_..._VITCS_early_mricrogl.py`, `figsup06d_1_..._VITCS_early_PREPROC.sh`, `figsup06d_2_..._VITCS_late_mricrogl.py` | Supp. Fig. 6 — VITCS-early / VITCS-late reliable-anatomy maps |

Figure scripts assume the corresponding `sNN_` analysis has already been run and expect `results/` to be populated; brain-rendering scripts (`*_mricrogl.py`) must be run from within MRIcroGL, not as standalone Python scripts.

---

## Notes on reproducibility

- The Training/Test split and the 10-fold CV assignment are controlled via saved `.mat` files provided in this repository (`data/training_data.mat`, `data/test_data.mat`, and one `data/10fold_CV_<model>.mat` per model - VITCS, VITCS-early, VITCS-late), so re-running the pipeline reproduces the exact published Training/Test partition and cross-validation folds. Set `USE_PUBLISHED_SPLIT = false` / `'new_10fold_CV', true` only if you intend to draw a fresh split (this will not reproduce the manuscript's numbers, since the original random seed was not recorded).
- **The bootstrap feature-stability analysis (`s05_VITCS_bootstrap_feature_stability.m` / `utils/run_bootstrap_feature_stability.m`, 5,000 resamples) is NOT seeded.** No random seed was recorded for it, so re-running this step will produce a very similar but not bit-for-bit identical thresholded weight map each time. This does not affect the Training/Test split or 10-fold CV, which are exactly reproducible as described above.
- `s09_comparison_existing_signatures.m` requires several third-party signature weight maps not distributed with CANlab (Liu-SUITAS, Wen-BeyondThreat, Wager-NPS); paths must be obtained from their original authors.

---
