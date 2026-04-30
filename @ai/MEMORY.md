# PocketRE — Project Memory Bank

Single source of truth for this thesis project. If a decision or feature does not align with this document, question it.

> **Companion document:** [`PROGRESS.md`](PROGRESS.md) tracks the chronological
> evolution of the experiments (iterations, results, diagnostics, next steps).
> Update PROGRESS at the end of each iteration.

---

## Project context

### Title (working title)

**PocketRE: A Local AI Assistant for Software Requirements Quality Analysis**

### Research approach

This project follows **Design Science Research (DSR)**:

- We build an artifact (a system/pipeline).
- We evaluate its effectiveness experimentally.
- The goal is **not** only implementation, but **evaluation**.

---

## Problem statement

Software requirements in natural language often suffer from:

- ambiguity
- lack of measurability
- optional or unclear statements
- conflicts between requirements

Manual analysis is slow and error-prone. We want to evaluate whether AI models can help automate this process.

---

## Objective

Build a **local** AI-based assistant capable of:

1. Detecting requirement defects
2. Detecting conflicts between requirements *(future)*
3. *(Optional / future)* Validating consistency between requirements and test cases

---

## Current scope (important)

Intentionally limited to:

**Requirement defect detection**

- ambiguous
- non-measurable
- optional

**Methods**

- NLI-based models as the primary approach
- Everything runs **locally** (no API dependency)

---

## Out of scope (for now)

- No UI
- No production system
- No full dataset engineering
- No training from scratch
- No large-scale infrastructure

This is a **research prototype** only.

---

## Project structure

```
tcc/
├── @ai/
│   └── MEMORY.md                 # this file — single source of truth
├── data/
│   └── dataset.json              # manually labeled requirements (ground truth)
├── scripts/
│   ├── lib/                      # shared library — all heavy lifting lives here
│   │   ├── labels.py             # label verbalization registry (BASELINE, IMPROVED, ...)
│   │   ├── io.py                 # JSON load/save helpers
│   │   ├── inference.py          # NLI + zero-shot HF pipeline wrappers
│   │   └── metrics.py            # P/R/F1, macro avg, threshold sweep, comparisons
│   ├── run_nli.py                # generic CLI runner — picks label set by name
│   ├── run_zeroshot.py           # generic CLI runner
│   ├── run_threshold_tuning.py   # generic CLI runner
│   ├── evaluate.py               # generic CLI evaluator
│   ├── compare_experiments.py    # side-by-side comparison utility
│   ├── baseline/                 # iteration 1 — baseline hypotheses (thin wrappers)
│   │   ├── run_nli.py
│   │   ├── run_zeroshot.py
│   │   └── evaluate.py
│   ├── improved/                 # iteration 2 — improved label verbalization (thin wrappers)
│   │   ├── run_nli_improved.py
│   │   ├── run_zeroshot_improved.py
│   │   └── evaluate_improved.py
│   └── threshold_tuning/         # iteration 3 — threshold tuning (BART only)
│       ├── run_threshold_tuning.py
│       └── select_best_thresholds.py
├── results/
│   ├── nli/
│   │   ├── baseline/
│   │   └── improved_labels/
│   └── zeroshot/
│       ├── baseline/
│       ├── improved_labels/
│       └── threshold_tuning/
├── src/                          # early experiments (kept for reference)
├── requirements.txt
└── .venv/
```

### Code organization principle

All shared logic (loading the dataset, calling the model, computing metrics,
saving results) lives in `scripts/lib/`. Every runner is a thin file
(~20–40 lines) that just configures parameters (model, label set, threshold,
output path) and delegates to the library.

Two equivalent ways to run an experiment:

- **Generic CLI** (`scripts/run_*.py --labels <name>`) — preferred for new
  variants; nothing to copy, just register the labels in `scripts/lib/labels.py`.
- **Per-iteration thin wrappers** (`scripts/baseline/`, `scripts/improved/`,
  `scripts/threshold_tuning/`) — preserved for traceability of past iterations.

---

## Implementation status

| Component | Status | Notes |
| --------- | ------ | ----- |
| Dataset (manual, 30 samples) | Done | `data/dataset.json` |
| NLI pipeline (`roberta-large-mnli`) | Done | `scripts/baseline/run_nli.py` |
| Zero-shot classification (`bart-large-mnli`) | Done | `scripts/baseline/run_zeroshot.py` |
| Evaluation (P / R / F1) | Done | `scripts/baseline/evaluate.py` |
| Improved labels — NLI | Done | `scripts/improved/run_nli_improved.py` |
| Improved labels — Zero-shot | Done | `scripts/improved/run_zeroshot_improved.py` |
| Improved labels — Evaluation | Done | `scripts/improved/evaluate_improved.py` |
| Experiment comparison utility | Done | `scripts/compare_experiments.py` |
| Threshold tuning (BART zero-shot) | Done | `scripts/threshold_tuning/run_threshold_tuning.py` |
| Best threshold selector | Done | `scripts/threshold_tuning/select_best_thresholds.py` |
| Local LLM | Not started | optional / future |

---

## Technical approach

We use **Natural Language Inference (NLI)**. The core idea: turn classification into an entailment problem.

For each requirement:

| Role        | Content              |
| ----------- | -------------------- |
| **Premise** | requirement text     |
| **Hypothesis** | defect description |

**Example**

- **Premise:** “The system should respond quickly.”
- **Hypothesis:** “This requirement contains vague or unclear terms that can be interpreted in multiple ways.”

**Interpretation**

- **ENTAILMENT** → defect present  
- **Otherwise** → defect not present  

---

## Defect hypotheses (label verbalization)

### Baseline hypotheses

Used in `scripts/baseline/`:

| Defect | Hypothesis |
| ------ | ---------- |
| `ambiguous` | "This requirement contains vague or unclear terms that can be interpreted in multiple ways." |
| `non_measurable` | "This requirement cannot be objectively measured or tested." |
| `optional` | "This requirement includes optional or non-mandatory behavior." |

### Improved hypotheses

Used in `scripts/improved/`. More specific — mentions concrete trigger words and criteria:

| Defect | Hypothesis |
| ------ | ---------- |
| `ambiguous` | "This requirement uses vague or subjective words such as clear, intuitive, fast, good, or efficient that can be interpreted differently by different people." |
| `non_measurable` | "This requirement does not define measurable acceptance criteria such as time limits, quantities, percentages, thresholds, or objective constraints." |
| `optional` | "This requirement uses optional language such as may, might, could, optionally, if necessary, or if appropriate." |

These matter — see "Important insight: label verbalization" below.

### Adding a new label variant

Source of truth: `scripts/lib/labels.py`. A label set is a `LabelSet`
dataclass bundling two things:

- `defects`    — defect name → hypothesis (used by NLI and zero-shot)
- `thresholds` — defect name → decision threshold (zero-shot only; NLI
                 ignores it because the model returns ENTAILMENT directly)

1. Add a new `LabelSet` at the bottom of `labels.py`:

   ```python
   CONCRETE_V3 = LabelSet(
       defects={
           "ambiguous": "...",
           "non_measurable": "...",
           "optional": "...",
       },
       thresholds={
           "ambiguous": 0.75,
           "non_measurable": 0.30,
           "optional": 0.70,
       },
   )
   ```

2. Register it in `LABEL_SETS` so the CLI can find it by name:

   ```python
   LABEL_SETS = {
       "baseline": BASELINE,
       "improved": IMPROVED,
       "concrete_v3": CONCRETE_V3,
   }
   ```

3. Run any pipeline pointing at the new variant — no other parameters needed:

   ```bash
   python scripts/run_nli.py --labels concrete_v3
   python scripts/run_zeroshot.py --labels concrete_v3
   python scripts/evaluate.py results/nli/concrete_v3/results_nli_concrete_v3.json
   python scripts/compare_experiments.py \
       results/nli/improved_labels/results_nli_improved.json \
       results/nli/concrete_v3/results_nli_concrete_v3.json
   ```

No new Python files required. There is **no global `DEFECT_TYPES` constant**:
each result file stores its own list under the `defect_types` key, and
`evaluate` / `compare_experiments` / `select_best_thresholds` discover it
from the file (with a fallback that infers from `predictions` keys for
older files).

### Result file format

Inference runners (NLI, zero-shot) write a self-describing envelope:

```json
{
  "defect_types": ["vague", "optional"],
  "items": [
    {"requirement": "...", "ground_truth": [...], "predictions": {...}}
  ]
}
```

Threshold tuning writes:

```json
{
  "defect_types": ["vague", "optional"],
  "metrics": {"vague": {"0.3": {...}, "0.4": {...}}, "optional": {...}}
}
```

See `scripts/lib/io.py` for `save_results`, `save_threshold_metrics`,
`unwrap_results`, `unwrap_threshold_metrics`.

---

## Models

We compare multiple approaches:

1. **NLI (primary)** — `roberta-large-mnli` ✔ implemented
2. **Zero-shot classification** — `facebook/bart-large-mnli` ✔ implemented
3. *(Optional later)* Local LLM

---

## Data strategy

1. Initial dataset: **30 manually labeled samples** in `data/dataset.json`.
2. Each sample includes:
   - requirement text
   - ground truth defects (list, may be empty for well-written requirements)

**Composition:**

- 12 requirements with `ambiguous` + `non_measurable`
- 8 requirements with `optional`
- 1 requirement with `ambiguous` only
- 9 well-written requirements (no defects)

**Format**

```json
{
  "requirement": "...",
  "defects": ["ambiguous"]
}
```

3. Expand the dataset later if needed.

---

## Evaluation

Metrics:

- Precision
- Recall
- F1 score

**Prediction mapping**

- **ENTAILMENT** → model predicts the defect exists  
- **Otherwise** → model predicts the defect does not exist  

---

## Design principles

- Keep everything simple
- Prefer clarity over complexity
- Avoid over-engineering
- Always align with the research goal

---

## Important insight: label verbalization

Model performance depends heavily on **how hypotheses are written** (label verbalization).

| Avoid | Prefer |
| ----- | ------ |
| “This requirement is ambiguous” | “This requirement contains vague or unclear terms that can be interpreted in multiple ways” |

---

## Use of this file

Reference this document for:

- all code decisions
- all architectural decisions
- all future features

Anything misaligned with this memory should be questioned before proceeding.

---

## Experiments

| Experiment | Variable changed | Scripts |
| ---------- | ---------------- | ------- |
| Baseline | Original hypotheses | `scripts/baseline/` |
| Improved labels | More specific verbalization | `scripts/improved/` |
| Threshold tuning | Decision threshold per defect (BART only) | `scripts/threshold_tuning/` |
| Improved v2 labels | Refined hypotheses + per-defect thresholds in `LabelSet` | `LABEL_SETS["improved_v2"]` |

Detailed timeline, per-experiment results and current diagnostics live in
[`PROGRESS.md`](PROGRESS.md).

---

## How to run

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Generic (preferred for new variants)

Pick a label set name registered in `scripts/lib/labels.py`. The label set
already carries its decision thresholds, so the runner needs no extra flags:

```bash
# NLI inference
python scripts/run_nli.py --labels improved

# Zero-shot inference (per-defect thresholds come from the label set)
python scripts/run_zeroshot.py --labels improved

# Threshold tuning sweep (BART zero-shot) — explores beyond the label set defaults
python scripts/run_threshold_tuning.py --labels improved \
    --thresholds 0.3 0.4 0.5 0.6 0.7

# Evaluate any results JSON
python scripts/evaluate.py results/nli/improved/results_nli_improved.json

# Compare two experiments
python scripts/compare_experiments.py \
    results/nli/baseline/results_nli.json \
    results/nli/improved_labels/results_nli_improved.json

# Pick best threshold per defect from a tuning sweep
python scripts/threshold_tuning/select_best_thresholds.py \
    results/zeroshot/threshold_tuning_improved/threshold_metrics.json
```

### Per-iteration thin wrappers (kept for traceability)

```bash
# ── Baseline ──
python scripts/baseline/run_nli.py
python scripts/baseline/run_zeroshot.py
python scripts/baseline/evaluate.py
python scripts/baseline/evaluate.py results/zeroshot/baseline/results_zeroshot.json

# ── Improved labels ──
python scripts/improved/run_nli_improved.py
python scripts/improved/run_zeroshot_improved.py
python scripts/improved/evaluate_improved.py
python scripts/improved/evaluate_improved.py results/zeroshot/improved_labels/results_zeroshot_improved.json

# ── Threshold tuning (BART zero-shot, improved labels) ──
python scripts/threshold_tuning/run_threshold_tuning.py
python scripts/threshold_tuning/select_best_thresholds.py
```
