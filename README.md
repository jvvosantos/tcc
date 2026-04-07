# PocketRE (TCC)

**PocketRE: A Local AI Assistant for Software Requirements Quality Analysis**

Prototype for a master’s thesis: detect common defects in natural-language requirements using **pre-trained models**, running **locally** (no cloud API). The project follows **Design Science Research (DSR)** — build an artifact, then evaluate it.

> Single source of truth for goals, scope, and hypotheses: [`@ai/MEMORY.md`](@ai/MEMORY.md).

## What it does

For each requirement in a small labeled set, the pipeline checks three defect types:

| Defect | Idea |
|--------|------|
| `ambiguous` | Vague or multi-interpretable wording |
| `non_measurable` | Cannot be objectively tested or measured |
| `optional` | Optional / non-mandatory behavior |

Two methods are implemented for comparison:

1. **NLI** — `roberta-large-mnli` (premise = requirement, hypothesis = defect description). **ENTAILMENT** ⇒ defect predicted.
2. **Zero-shot** — `facebook/bart-large-mnli` with the same hypotheses as candidate labels; score > 0.5 ⇒ **ENTAILMENT** (aligned with the evaluation script).

## Requirements

- Python 3.10+ (project uses 3.10 in `.venv`)
- GPU optional; CPU works but is slower for large models
- First run downloads model weights from Hugging Face (~1–2 GB per model depending on cache)

## Setup

```bash
cd /path/to/tcc
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Dependencies: `torch`, `transformers` (see `requirements.txt`).

## Project layout

```
tcc/
├── @ai/MEMORY.md              # research memory / conventions
├── data/
│   └── dataset.json           # ground-truth requirements + defect labels
├── scripts/baseline/
│   ├── run_nli.py             # RoBERTa NLI inference
│   ├── run_zeroshot.py        # BART zero-shot inference
│   └── evaluate.py            # precision, recall, F1 (+ macro average)
├── results/                   # saved experiment outputs (e.g. baselines)
│   ├── nli/baseline/
│   └── zeroshot/baseline/
├── src/                       # small exploratory scripts
├── requirements.txt
└── .gitignore
```

Running the baseline scripts writes JSON predictions under `data/` (`results_nli.json`, `results_zeroshot.json`). You can copy or version outputs under `results/` for reproducibility.

## Run

From the repository root:

```bash
source .venv/bin/activate

# NLI (writes data/results_nli.json)
python scripts/baseline/run_nli.py

# Zero-shot (writes data/results_zeroshot.json)
python scripts/baseline/run_zeroshot.py

# Evaluation — default: data/results_nli.json
python scripts/baseline/evaluate.py

python scripts/baseline/evaluate.py data/results_zeroshot.json
python scripts/baseline/evaluate.py results/nli/baseline/results_nli.json
```

**Prediction rule for metrics:** **ENTAILMENT** = positive; **NEUTRAL** or **CONTRADICTION** = negative.

## Dataset format

Each line in `data/dataset.json` is one object:

```json
{
  "requirement": "The system shall …",
  "defects": ["ambiguous", "non_measurable"]
}
```

Use an empty list `[]` for requirements with no labeled defects.

## Scope

This is a **research prototype**, not production software: no UI, no training from scratch, no large-scale data pipeline. See `@ai/MEMORY.md` for what is in and out of scope.

## License

Not specified in this repository; add a `LICENSE` if you publish the code.
