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
> This produces `manuscript.pdf` (via Typst) and `manuscript.docx`. Requirements and data dependencies are listed below.

---

## Overview

This repository contains all materials for our registered report stage 1 protocol examining how the toxicity dose of a social media feed affects ad effectiveness and brand safety. We apply a dose-response design to a Digital In-Context Experiment (DICE) that manipulates toxicity doses between subjects exogenously.

---

## Repository structure

```
.
├── data/                          # Data from the stimulus rating study
│   ├── raw/                       # Raw oTree exports (read-only)
│   ├── simulations/               # Power simulation outputs (reproducible from simulate.qmd)
│   └── codebook.md                # Variable-level codebook for the DICE experiment
│
├── literature/                    # BibTeX bibliography (_references.bib); PDFs not tracked
│
├── pilot-dice/                    # Pilot DICE experiment
│   ├── analyses/                  # Analysis script (analyses.qmd) and twolines.R helper
│   ├── data/
│   │   ├── processed/             # Participant-level pilot data (raw data not shared, GDPR)
│   │   └── stimuli/               # Pilot stimulus corpus
│   ├── otree/                     # Archived pilot oTree application (.otreezip)
│   ├── pre-reg/                   # Pre-registration document
│   ├── prolific/                  # Prolific recruitment summaries
│   └── qualtrics/                 # Qualtrics survey export (.qsf)
│
├── software/                      # Main DICE oTree experiment
│   ├── DICE/                      # App code, page templates, and stimulus corpus
│   ├── settings.py                # oTree session configuration
│   └── requirements.txt           # Python dependencies
│
├── stimuli/                       # Stimulus generation and validation pipeline
│   ├── generation/                # Quarto scripts for generating and classifying posts
│   ├── analyses/                  # Corpus evaluation script (stimuli-evaluation.qmd)
│   └── rating-study/              # Human toxicity validation study
│       ├── data/                  # Rating data and codebook
│       └── prolific/              # Prolific recruitment summaries
│
├── study-1-upworthy/              # Observational study (Upworthy Research Archive)
│   ├── data/processed/            # Processed headlines with toxicity scores
│   └── scripts/                   # Data pipeline (upworthy.qmd) and helpers.R
│
└── writeup/
    ├── IJRM-preprint/
    │   ├── manuscript.qmd         # Manuscript source (also the analysis script)
    │   └── figures/               # Design mockups and screenshots
    ├── documentation/             # Stimulus documentation
    └── Submission/                # Journal submission files
```

---

## R packages for analysis

R version 4.4.1 is required. Package versions are pinned via [`groundhog`](https://groundhogr.com) (date `2026-01-01`) and installed automatically on first render — no manual installation needed.

| Package | Version | Purpose |
|---|---|---|
| `data.table` | 1.18.0 | Data loading and wrangling |
| `ggplot2` | 4.0.1 | Figures |
| `patchwork` | 1.3.2 | Combining plots |
| `fixest` | 0.13.2 | Fixed-effects regressions |
| `scales` | 1.4.0 | Number formatting |
| `mgcv` | 1.9.4 | Cubic spline smoother (two-lines test) |
| `MOTE` | 1.2.2 | Effect sizes |
| `flextable` | 0.9.10 | Tables |
| `stringr` | 1.6.0 | String operations |
| `english` | 1.2.6 | Number-to-word conversion |
| `modelsummary` | 2.5.0 | Regression tables |
| `rstatix` | 0.7.3 | Summary statistics |
| `gt` | 1.2.0 | Tables |
| `sandwich` | 3.1.1 | Robust standard errors |
| `lmtest` | 0.9.40 | Coefficient tests |
| `margins` | 0.3.28 | Marginal effects |

**Quarto**
Version 1.6 or later. The Typst PDF backend is used; no LaTeX installation required. The `preprint-typst` extension is bundled in `writeup/IJRM-preprint/_extensions/`.

---

## Data requirements

The following files are not tracked and must be obtained separately before rendering:

| File | Source |
|---|---|
| `study-1-upworthy/data/raw/upworthy-archive-confirmatory-packages-03.12.2020.csv` | [Upworthy Research Archive](https://doi.org/10.7910/DVN/CHMUYZ) |

All other data files required by the manuscript are included in this repository.

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

**The edited version is the corpus used in the main study.** The original is retained for transparency. The active corpus path is set in `settings.py`.

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