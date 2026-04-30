"""PocketRE — Generic evaluator.

Loads a results JSON file (produced by ``run_nli`` or ``run_zeroshot``) and
prints per-defect Precision / Recall / F1 plus the macro average.

Example
-------
    python scripts/evaluate.py results/nli/improved/results_nli_improved.json
"""

import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import io, metrics  # noqa: E402


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/evaluate.py <results.json>")
        sys.exit(1)

    results_path = sys.argv[1]
    results = io.load_results(results_path)
    metrics.print_evaluation(
        results, header=f"Evaluating: {os.path.basename(results_path)}"
    )


if __name__ == "__main__":
    main()
