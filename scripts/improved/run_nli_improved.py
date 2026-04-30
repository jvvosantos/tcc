"""PocketRE — NLI defect detection (improved labels).

Iteration 2. Equivalent to::

    python scripts/run_nli.py --labels improved

See @ai/MEMORY.md § "Defect hypotheses (label verbalization)".
"""

import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import inference, io, labels  # noqa: E402

DATASET_PATH = os.path.join(ROOT_DIR, "data", "dataset.json")
RESULTS_PATH = os.path.join(
    ROOT_DIR, "results", "nli", "improved_labels", "results_nli_improved.json"
)

MODEL_NAME = "roberta-large-mnli"
LABELS = labels.IMPROVED


def main():
    dataset = io.load_dataset(DATASET_PATH)
    results = inference.run_nli(MODEL_NAME, dataset, LABELS)
    io.save_results(RESULTS_PATH, list(LABELS.defects.keys()), results)
    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
