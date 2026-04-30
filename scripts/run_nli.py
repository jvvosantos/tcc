"""PocketRE — Generic NLI runner.

Picks a label set from ``scripts/lib/labels.py`` by name and runs NLI
inference. The output JSON lives at::

    results/nli/<labels>/results_nli_<labels>.json

unless ``--out`` is provided.

Example
-------
    python scripts/run_nli.py --labels improved
    python scripts/run_nli.py --labels concrete_v3 --model roberta-large-mnli
"""

import argparse
import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import inference, io, labels  # noqa: E402

DATASET_PATH = os.path.join(ROOT_DIR, "data", "dataset.json")
DEFAULT_MODEL = "roberta-large-mnli"


def parse_args():
    parser = argparse.ArgumentParser(description="Run NLI defect detection.")
    parser.add_argument(
        "--labels",
        required=True,
        help=f"Label set name. Available: {sorted(labels.LABEL_SETS)}",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="HF model name.")
    parser.add_argument(
        "--out",
        default=None,
        help="Output JSON path. Defaults to results/nli/<labels>/results_nli_<labels>.json.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    label_set = labels.get(args.labels)
    out_path = args.out or io.default_results_path(ROOT_DIR, "nli", args.labels)

    dataset = io.load_dataset(DATASET_PATH)
    results = inference.run_nli(args.model, dataset, label_set)
    io.save_json(out_path, results)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
