"""PocketRE — Compare two experiments side-by-side.

Loads two results JSON files, computes metrics for each, and prints a
side-by-side comparison with the per-defect (and macro) difference.

Usage
-----
    python scripts/compare_experiments.py <baseline.json> <improved.json>

Examples
--------
    python scripts/compare_experiments.py \
        results/nli/baseline/results_nli.json \
        results/nli/improved_labels/results_nli_improved.json

    python scripts/compare_experiments.py \
        results/zeroshot/baseline/results_zeroshot.json \
        results/zeroshot/improved_labels/results_zeroshot_improved.json
"""

import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import io, metrics  # noqa: E402


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/compare_experiments.py <baseline.json> <improved.json>")
        sys.exit(1)

    baseline_path, improved_path = sys.argv[1], sys.argv[2]
    baseline = io.load_results(baseline_path)
    improved = io.load_results(improved_path)

    print(f"Baseline:  {os.path.basename(baseline_path)}")
    print(f"Improved:  {os.path.basename(improved_path)}")
    print(f"Samples:   {len(baseline)} (baseline) / {len(improved)} (improved)")
    print()

    metrics.print_comparison(baseline, improved)


if __name__ == "__main__":
    main()
