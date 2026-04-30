"""PocketRE — Zero-shot defect detection (improved labels).

Iteration 2. Equivalent to::

    python scripts/run_zeroshot.py --labels improved
"""

import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import inference, io, labels  # noqa: E402

DATASET_PATH = os.path.join(ROOT_DIR, "data", "dataset.json")
RESULTS_PATH = os.path.join(
    ROOT_DIR, "results", "zeroshot", "improved_labels", "results_zeroshot_improved.json"
)

MODEL_NAME = "facebook/bart-large-mnli"
LABELS = labels.IMPROVED


def main():
    dataset = io.load_dataset(DATASET_PATH)
    results = inference.run_zeroshot(MODEL_NAME, dataset, LABELS)
    io.save_results(RESULTS_PATH, list(LABELS.defects.keys()), results)
    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
