"""PocketRE — Rule-based defect detection (rules_v1 lexicon).

Iteration 7. Equivalent to::

    python scripts/run_rules.py --labels rules_v1

Lexical baseline: each defect has a list of trigger terms; a requirement
is flagged when any term matches as a whole word (case-insensitive).
This is the "regex baseline" against which BART zero-shot must justify
its compute cost — see @ai/PROGRESS.md § "M10 — Rule-based baseline".
"""

import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import io, labels, rules  # noqa: E402

RESULTS_PATH = os.path.join(
    ROOT_DIR, "results", "rules", "rules_v1", "results_rules_rules_v1.json"
)

LABELS = labels.RULES_V1


def main():
    dataset = io.load_dataset(os.path.join(ROOT_DIR, LABELS.dataset))
    results = rules.run_rules(dataset, LABELS)
    io.save_results(RESULTS_PATH, list(LABELS.terms.keys()), results)
    print(f"\nResults saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
