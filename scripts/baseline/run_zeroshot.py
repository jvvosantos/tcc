"""
PocketRE — Zero-shot classification for requirement defect detection.

Uses facebook/bart-large-mnli via the zero-shot-classification pipeline.
This is the second method for comparison against the NLI approach (run_nli.py).

For each requirement, the model scores each defect hypothesis independently
(multi_label=True). Internally, BART-MNLI treats each hypothesis as an
NLI entailment problem — the returned score is the entailment probability.

Score > 0.5 → ENTAILMENT (defect predicted)
Score ≤ 0.5 → NEUTRAL    (defect not predicted)
"""

import json
import os
from transformers import pipeline

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
DATASET_PATH = os.path.join(DATA_DIR, "dataset.json")
RESULTS_PATH = os.path.join(DATA_DIR, "results_zeroshot.json")

MODEL_NAME = "facebook/bart-large-mnli"

ENTAILMENT_THRESHOLD = 0.5

# Same hypotheses as run_nli.py — label verbalization matters (see MEMORY.md)
DEFECTS = {
    "ambiguous": "This requirement contains vague or unclear terms that can be interpreted in multiple ways.",
    "non_measurable": "This requirement cannot be objectively measured or tested.",
    "optional": "This requirement includes optional or non-mandatory behavior.",
}


def load_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def classify_requirement(classifier, requirement, defects):
    """Run zero-shot classification for a single requirement against all defect hypotheses."""
    hypotheses = list(defects.values())
    defect_names = list(defects.keys())

    # multi_label=True gives independent scores per hypothesis (no softmax across labels)
    # hypothesis_template="{}" passes our hypotheses verbatim instead of wrapping them
    result = classifier(
        requirement,
        candidate_labels=hypotheses,
        hypothesis_template="{}",
        multi_label=True,
    )

    # Map scores back to defect names
    predictions = {}
    for hypothesis, score in zip(result["labels"], result["scores"]):
        defect_name = defect_names[hypotheses.index(hypothesis)]
        label = "ENTAILMENT" if score > ENTAILMENT_THRESHOLD else "NEUTRAL"
        predictions[defect_name] = {
            "label": label,
            "score": round(score, 4),
        }

    return predictions


def main():
    print(f"Loading model: {MODEL_NAME}")
    classifier = pipeline("zero-shot-classification", model=MODEL_NAME)

    dataset = load_dataset(DATASET_PATH)
    print(f"Loaded {len(dataset)} requirements from dataset.")

    results = []
    for i, item in enumerate(dataset):
        req = item["requirement"]
        print(f"  [{i + 1}/{len(dataset)}] {req[:80]}...")

        predictions = classify_requirement(classifier, req, DEFECTS)
        results.append({
            "requirement": req,
            "ground_truth": item["defects"],
            "predictions": predictions,
        })

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
