"""PocketRE — Select best per-defect thresholds and compute combined macro F1.

Reads ``threshold_metrics.json`` and reports:
  - best threshold per defect (by F1)
  - the macro-average P/R/F1 obtained by combining the best thresholds

Usage
-----
    python scripts/threshold_tuning/select_best_thresholds.py
    python scripts/threshold_tuning/select_best_thresholds.py path/to/threshold_metrics.json
"""

import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import io, metrics  # noqa: E402
from scripts.lib.labels import DEFECT_TYPES  # noqa: E402

DEFAULT_METRICS = os.path.join(
    ROOT_DIR, "results", "zeroshot", "threshold_tuning", "threshold_metrics.json"
)


def find_best_threshold(defect_metrics):
    """Return ``(threshold_key, metrics_dict)`` with highest F1 for a defect."""
    return max(defect_metrics.items(), key=lambda kv: kv[1]["f1"])


def main():
    metrics_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_METRICS
    all_metrics = io.load_results(metrics_path)

    print("PocketRE — Best Thresholds per Defect")
    print(f"Source: {metrics_path}")
    print("=" * 55)

    best = {}
    for defect in DEFECT_TYPES:
        threshold_key, m = find_best_threshold(all_metrics[defect])
        best[defect] = m

        print(f"\nDefect: {defect}")
        print(f"  Best threshold: {threshold_key}")
        print(f"  Precision:      {m['precision']}")
        print(f"  Recall:         {m['recall']}")
        print(f"  F1:             {m['f1']}")
        print(f"  (TP={m['tp']}  FP={m['fp']}  FN={m['fn']}  TN={m['tn']})")

    macro = metrics.macro_average(best)
    print("\n" + "=" * 55)
    print("COMBINED MACRO AVERAGE (best threshold per defect)")
    print(f"  Precision: {macro['precision']}")
    print(f"  Recall:    {macro['recall']}")
    print(f"  F1:        {macro['f1']}")
    print("=" * 55)


if __name__ == "__main__":
    main()
