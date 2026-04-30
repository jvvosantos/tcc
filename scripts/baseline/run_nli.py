"""PocketRE — NLI defect detection (baseline labels).

Iteration 1. Equivalent to::

    python scripts/run_nli.py --labels baseline

Kept as a standalone script so each experiment iteration has a dedicated
entry point in version control.
"""

import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import inference, io, labels  # noqa: E402

DATASET_PATH = os.path.join(ROOT_DIR, "data", "dataset.json")
RESULTS_PATH = os.path.join(ROOT_DIR, "results", "nli", "baseline", "results_nli.json")

MODEL_NAME = "roberta-large-mnli"
LABELS = labels.BASELINE


def main():
    dataset = io.load_dataset(DATASET_PATH)
    results = inference.run_nli(MODEL_NAME, dataset, LABELS)
    io.save_json(RESULTS_PATH, results)
    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
