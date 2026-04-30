"""I/O helpers for PocketRE experiments."""

import json
import os


def load_dataset(path):
    """Load the labeled requirements dataset (list of {requirement, defects})."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_results(path):
    """Load any JSON results file produced by the runners."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    """Write JSON to ``path``, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def default_results_path(root_dir, method, variant):
    """Conventional path for a runner's output JSON file.

    e.g. ``default_results_path(ROOT, "nli", "improved")`` ->
    ``<root>/results/nli/improved/results_nli_improved.json``.
    """
    return os.path.join(
        root_dir, "results", method, variant, f"results_{method}_{variant}.json"
    )
