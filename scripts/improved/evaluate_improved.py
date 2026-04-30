"""PocketRE — Evaluate improved NLI results (default).

Equivalent to::

    python scripts/evaluate.py results/nli/improved_labels/results_nli_improved.json

Pass a different path as a positional argument to evaluate other files.
"""

import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import io, metrics  # noqa: E402

DEFAULT_RESULTS = os.path.join(
    ROOT_DIR, "results", "nli", "improved_labels", "results_nli_improved.json"
)


def main():
    results_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RESULTS
    results = io.load_results(results_path)
    metrics.print_evaluation(
        results, header=f"Evaluating: {os.path.basename(results_path)}"
    )


if __name__ == "__main__":
    main()
