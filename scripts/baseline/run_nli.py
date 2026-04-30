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

RESULTS_PATH = os.path.join(ROOT_DIR, "results", "nli", "baseline", "results_nli.json")

MODEL_NAME = "roberta-large-mnli"
LABELS = labels.BASELINE


def main():
    dataset = io.load_dataset(os.path.join(ROOT_DIR, LABELS.dataset))
    results = inference.run_nli(MODEL_NAME, dataset, LABELS)
    io.save_results(RESULTS_PATH, list(LABELS.defects.keys()), results)
    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
