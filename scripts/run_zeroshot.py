"""PocketRE — Generic zero-shot runner.

Picks a label set from ``scripts/lib/labels.py`` by name and runs zero-shot
classification. Per-defect decision thresholds come from the label set
itself (``LabelSet.thresholds``).

Output JSON path::

    results/zeroshot/<labels>/results_zeroshot_<labels>.json

unless ``--out`` is provided.

Example
-------
    python scripts/run_zeroshot.py --labels improved
    python scripts/run_zeroshot.py --labels concrete_v3 --out path/to/file.json
"""

import argparse
import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import inference, io, labels  # noqa: E402

DEFAULT_MODEL = "facebook/bart-large-mnli"


def parse_args():
    parser = argparse.ArgumentParser(description="Run zero-shot defect detection.")
    parser.add_argument(
        "--labels",
        required=True,
        help=f"Label set name. Available: {sorted(labels.LABEL_SETS)}",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="HF model name.")
    parser.add_argument(
        "--out",
        default=None,
        help="Output JSON path. Defaults to results/zeroshot/<labels>/results_zeroshot_<labels>.json.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    label_set = labels.get(args.labels)
    out_path = args.out or io.default_results_path(ROOT_DIR, "zeroshot", args.labels)

    dataset = io.load_dataset(os.path.join(ROOT_DIR, label_set.dataset))
    results = inference.run_zeroshot(args.model, dataset, label_set)
    io.save_results(out_path, list(label_set.defects.keys()), results)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
