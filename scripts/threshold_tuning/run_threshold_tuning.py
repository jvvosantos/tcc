"""PocketRE — Threshold tuning for zero-shot defect detection (improved labels).

Iteration 3. Equivalent to::

    python scripts/run_threshold_tuning.py --labels improved
"""

import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import inference, io, labels, metrics  # noqa: E402
from scripts.run_threshold_tuning import write_summary  # noqa: E402

DATASET_PATH = os.path.join(ROOT_DIR, "data", "dataset.json")
OUTPUT_DIR = os.path.join(ROOT_DIR, "results", "zeroshot", "threshold_tuning")

MODEL_NAME = "facebook/bart-large-mnli"
LABELS = labels.IMPROVED
LABELS_NAME = "improved"
THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7]


def main():
    dataset = io.load_dataset(DATASET_PATH)
    scored_items = inference.collect_zeroshot_scores(MODEL_NAME, dataset, LABELS)

    metrics_dict = metrics.evaluate_thresholds(
        scored_items, labels.DEFECT_TYPES, THRESHOLDS
    )

    metrics_path = os.path.join(OUTPUT_DIR, "threshold_metrics.json")
    io.save_json(metrics_path, metrics_dict)
    print(f"\nMetrics saved to {metrics_path}")

    summary_path = os.path.join(OUTPUT_DIR, "threshold_summary.txt")
    write_summary(
        metrics_dict, labels.DEFECT_TYPES, THRESHOLDS,
        summary_path, MODEL_NAME, LABELS_NAME,
    )
    print(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    main()
