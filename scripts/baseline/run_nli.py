"""
PocketRE — NLI-based requirement defect detection.

Uses roberta-large-mnli to classify each requirement against
known defect descriptions via Natural Language Inference.

Premise:    the requirement text
Hypothesis: a defect description

ENTAILMENT  → defect likely present
NEUTRAL/CONTRADICTION → defect likely absent
"""

import json
import os
from transformers import pipeline

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATASET_PATH = os.path.join(DATA_DIR, "dataset.json")
RESULTS_PATH = os.path.join(DATA_DIR, "results_nli.json")

MODEL_NAME = "roberta-large-mnli"

# Carefully worded hypotheses — label verbalization matters (see MEMORY.md)
DEFECTS = {
    "ambiguous": "This requirement contains vague or unclear terms that can be interpreted in multiple ways.",
    "non_measurable": "This requirement cannot be objectively measured or tested.",
    "optional": "This requirement includes optional or non-mandatory behavior.",
}


def load_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def classify_requirement(nli_pipeline, requirement, defects):
    """Run NLI for a single requirement against all defect hypotheses."""
    predictions = {}
    for defect_name, hypothesis in defects.items():
        result = nli_pipeline(
            {"text": requirement, "text_pair": hypothesis},
            top_k=None,
        )
        # top_k=None returns all labels; pick the highest-scoring one
        best = max(result, key=lambda x: x["score"])
        predictions[defect_name] = {
            "label": best["label"],
            "score": round(best["score"], 4),
        }
    return predictions


def main():
    print(f"Loading model: {MODEL_NAME}")
    nli = pipeline("text-classification", model=MODEL_NAME)

    dataset = load_dataset(DATASET_PATH)
    print(f"Loaded {len(dataset)} requirements from dataset.")

    results = []
    for i, item in enumerate(dataset):
        req = item["requirement"]
        print(f"  [{i + 1}/{len(dataset)}] {req[:80]}...")

        predictions = classify_requirement(nli, req, DEFECTS)
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
