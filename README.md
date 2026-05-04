# Advertising in Toxic Feeds: Ad Effectiveness and Brand Safety

Registered Report Stage 1 Protocol

---

## Reproducing the manuscript

> **One command reproduces the entire paper.**
> 
> `writeup/IJRM-preprint/manuscript.qmd` is simultaneously the manuscript source and the complete analysis script — every number, table, and figure is computed inline. Run from the project root:
> 
> ```bash
> quarto render writeup/IJRM-preprint/manuscript.qmd
> ```
> 
> This produces `manuscript.pdf` (via Typst) and `manuscript.docx`. Requirements and data dependencies are detailed in the [Software requirements](#software-requirements) and [Data requirements](#data-requirements) sections below.

---

## Overview

This repository contains all materials for our registered report stage 1 protocol examining how the toxicity dose  of a 
social media feed affects ad effectiveness and brand safety. We apply a dose-response design to a Digital In-Context Experiment
(DICE) that manipulates toxicity doses between subjects exogeneously.

---

## Repository structure

```
.
├── data/                          # Data from the DICE experiment and stimulus rating study
│   ├── raw/                       # Raw oTree exports (read-only)
│   ├── simulations/               # Power simulation outputs (reproducible from simulate.qmd)
│   └── codebook.md                # Variable-level codebook for the DICE experiment
│
├── literature/                    # BibTeX bibliography (_references.bib); PDFs not tracked
│
├── misc/                          # Supporting figures and reference materials
│
├── pilot-dice/                    # Pilot DICE experiment
│   ├── analyses/                  # Analysis script (analyses.qmd) and twolines.R helper
│   ├── data/processed/            # Participant-level pilot data
│   └── qualtrics/                 # Qualtrics survey export (.qsf)
│
├── software/                      # Main DICE oTree experiment
│   ├── DICE/                      # App code, templates, and stimulus corpus
│   ├── settings.py                # oTree session configuration
│   └── requirements.txt           # Python dependencies
│
├── stimuli/                       # Stimulus generation and validation pipeline
│   ├── generation/                # Quarto scripts for generating and classifying posts
│   ├── rating-study/              # Human validation study
│   │   ├── data/                  # Raw rating data and codebook
│   │   └── software/              # oTree app for the rating task
│   └── analyses/                  # Corpus evaluation scripts
│
├── study-1-upworthy/              # Observational study (Upworthy Research Archive)
│   ├── data/processed/            # Processed headlines with toxicity scores
│   └── scripts/                   # Analysis scripts (upworthy.qmd, helpers.R)
│
└── writeup/
    ├── IJRM-preprint/
    │   └── manuscript.qmd         # Manuscript source (also the analysis script)
    └── Submission/                # Journal submission files
```

---

## Reproducing the manuscript

The manuscript follows a literate programming approach: `writeup/IJRM-preprint/manuscript.qmd` is simultaneously the source file for the paper and the complete analysis script. Rendering it reproduces every number, table, and figure in the manuscript.

```bash
quarto render writeup/IJRM-preprint/manuscript.qmd
```

This produces `manuscript.pdf` (via Typst) and `manuscript.docx`.

### Software requirements

**R**  
Version 4.4.1. Packages are managed via [`groundhog`](https://groundhogr.com) with date `2026-01-01`, which restores exact package versions automatically on first render. Required packages (installed automatically):

`magrittr`, `data.table`, `ggplot2`, `patchwork`, `stringr`, `english`, `MOTE`, `flextable`, `fixest`, `modelsummary`, `scales`, `rstatix`, `gt`, `mgcv`, `sandwich`, `lmtest`, `margins`

**Quarto**  
Version 1.6 or later. The Typst PDF backend is used; no LaTeX installation required. The `preprint-typst` extension is bundled in `writeup/IJRM-preprint/_extensions/`.

### Data requirements

The following files must be present before rendering (not tracked due to size or privacy):

| File | Source |
|---|---|
| `study-1-upworthy/data/raw/upworthy-archive-confirmatory-packages-03.12.2020.csv` | [Upworthy Research Archive](https://doi.org/10.7910/DVN/CHMUYZ) |
| `study-1-upworthy/data/processed/headlines_with_txicity_scores.csv` | Derived from the above via `study-1-upworthy/scripts/upworthy.qmd` |
| `data/simulations/simulations.csv` | Reproducible from `data/simulations/simulate.qmd` |
| `data/simulations/power_sim_*.csv` | Reproducible from `data/simulations/simulate.qmd` |

Pilot DICE data (`pilot-dice/data/raw/`) are not shared publicly to protect participant privacy (GDPR). Processed pilot outputs (`pilot-dice/data/processed/`) are included.

---

## Running the experiments

Both experiments run on [oTree](https://www.otree.org) (version 5.x, Python 3.11.9).

### DICE feed experiment (main study)

```bash
cd software/
pip install -r requirements.txt
otree devserver
```

App: `DICE`. The stimulus corpus is in `software/DICE/static/data/`. Two versions are stored there:

- `toxic_movie_reactions.csv` — original generated corpus
- `toxic_movie_reactions_edited.csv` — version after manual review (replacing the term *flick* with *movie*/*film*, correcting GPT-4o-mini stance classifications, and minor phrasing edits; see `software/DICE/static/data/README.md` for details)

**The edited version is the corpus used in the main study.** The original is retained for transparency. Session configuration, including the active corpus path, is in `settings.py`.

### Stimulus rating study

```bash
cd stimuli/software/
pip install -r requirements.txt
otree devserver
```

App: `ratings`. The stimulus corpus is at `stimuli/software/ratings/corpus.csv`.

### Data export

After data collection, export participant data from the oTree admin panel (`Data > Custom export > DICE` or `ratings`). The resulting CSV matches the variable definitions in the codebooks:

- DICE experiment: `data/codebook.md`
- Rating study: `stimuli/rating-study/data/codebook.md`