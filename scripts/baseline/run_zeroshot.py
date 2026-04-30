"""PocketRE — Zero-shot defect detection (baseline labels).

Iteration 1. Equivalent to::

    python scripts/run_zeroshot.py --labels baseline
"""

import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import inference, io, labels  # noqa: E402

RESULTS_PATH = os.path.join(ROOT_DIR, "results", "zeroshot", "baseline", "results_zeroshot.json")

MODEL_NAME = "facebook/bart-large-mnli"
LABELS = labels.BASELINE


def main():
    dataset = io.load_dataset(os.path.join(ROOT_DIR, LABELS.dataset))
    results = inference.run_zeroshot(MODEL_NAME, dataset, LABELS)
    io.save_results(RESULTS_PATH, list(LABELS.defects.keys()), results)
    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
