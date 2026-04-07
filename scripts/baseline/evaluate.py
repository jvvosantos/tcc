"""
PocketRE — Evaluation script.

Loads results from an NLI or zero-shot run and computes per-defect
and macro-average Precision, Recall, and F1 score.

Usage:
  python scripts/baseline/evaluate.py
  python scripts/baseline/evaluate.py data/results_nli.json
  python scripts/baseline/evaluate.py results/nli/baseline/results_nli.json

Prediction mapping (see MEMORY.md):
  ENTAILMENT            → predicted positive
  NEUTRAL/CONTRADICTION → predicted negative
"""

import json
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
DEFAULT_RESULTS = os.path.join(DATA_DIR, "results_nli.json")

DEFECT_TYPES = ["ambiguous", "non_measurable", "optional"]


def load_results(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_metrics(results, defect_type):
    """Compute precision, recall, and F1 for a single defect type."""
    tp = fp = fn = tn = 0

    for item in results:
        actual_positive = defect_type in item["ground_truth"]
        predicted_positive = item["predictions"][defect_type]["label"] == "ENTAILMENT"

        if actual_positive and predicted_positive:
            tp += 1
        elif not actual_positive and predicted_positive:
            fp += 1
        elif actual_positive and not predicted_positive:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }


def main():
    results_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RESULTS
    results = load_results(results_path)

    filename = os.path.basename(results_path)
    print(f"Evaluating: {filename}")
    print(f"Loaded {len(results)} results.\n")
    print("=" * 50)

    all_metrics = {}

    for defect in DEFECT_TYPES:
        metrics = compute_metrics(results, defect)
        all_metrics[defect] = metrics

        print(f"Defect: {defect}")
        print(f"  Precision: {metrics['precision']}")
        print(f"  Recall:    {metrics['recall']}")
        print(f"  F1:        {metrics['f1']}")
        print(f"  (TP={metrics['tp']}  FP={metrics['fp']}  FN={metrics['fn']}  TN={metrics['tn']})")
        print("-" * 50)

    macro_precision = sum(m["precision"] for m in all_metrics.values()) / len(all_metrics)
    macro_recall = sum(m["recall"] for m in all_metrics.values()) / len(all_metrics)
    macro_f1 = sum(m["f1"] for m in all_metrics.values()) / len(all_metrics)

    print(f"MACRO AVERAGE")
    print(f"  Precision: {round(macro_precision, 4)}")
    print(f"  Recall:    {round(macro_recall, 4)}")
    print(f"  F1:        {round(macro_f1, 4)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
