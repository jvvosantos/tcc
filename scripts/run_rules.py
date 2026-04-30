"""PocketRE — Generic rule-based runner.

Picks a label set from ``scripts/lib/labels.py`` by name and runs lexical
rule-based defect detection over its dataset. The label set must define
``terms`` (mapping defect_name -> list of trigger terms); raises if it
doesn't.

Output JSON path::

    results/rules/<labels>/results_rules_<labels>.json

unless ``--out`` is provided.

Example
-------
    python scripts/run_rules.py --labels rules_v1
    python scripts/run_rules.py --labels rules_v1 --out path/to/file.json
"""

import argparse
import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import io, labels, rules  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser(description="Run rule-based defect detection.")
    parser.add_argument(
        "--labels",
        required=True,
        help=f"Label set name. Available: {sorted(labels.LABEL_SETS)}",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output JSON path. Defaults to results/rules/<labels>/results_rules_<labels>.json.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    label_set = labels.get(args.labels)
    out_path = args.out or io.default_results_path(ROOT_DIR, "rules", args.labels)

    dataset = io.load_dataset(os.path.join(ROOT_DIR, label_set.dataset))
    results = rules.run_rules(dataset, label_set)
    io.save_results(out_path, list(label_set.terms.keys()), results)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
