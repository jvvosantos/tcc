"""I/O helpers for PocketRE experiments.

Result file format
------------------
Inference runners (NLI, zero-shot) and the threshold-tuning runner write
**self-describing JSON** with ``defect_types`` as the first key, so that
evaluation scripts know which defects to look at without consulting any
external constant.

For inference runners (``run_nli``, ``run_zeroshot``)::

    {
        "defect_types": ["vague", "optional"],
        "items": [
            {"requirement": "...", "ground_truth": [...], "predictions": {...}},
            ...
        ]
    }

For threshold tuning (``run_threshold_tuning``)::

    {
        "defect_types": ["vague", "optional"],
        "metrics": {
            "vague": {"0.3": {...}, "0.4": {...}, ...},
            "optional": {"0.3": {...}, ...}
        }
    }

Backwards compatibility: ``unwrap_results`` accepts the legacy "list of items"
format and infers ``defect_types`` from the keys of the first item's
``predictions`` dict, so that older result files keep working until they are
re-generated.
"""

import json
import os


def load_dataset(path):
    """Load the labeled requirements dataset (list of {requirement, defects})."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_results(path):
    """Load any JSON results file produced by the runners (envelope or legacy)."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    """Write JSON to ``path``, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_results(path, defect_types, items):
    """Write inference results in the self-describing envelope format."""
    save_json(path, {"defect_types": list(defect_types), "items": items})


def save_threshold_metrics(path, defect_types, metrics):
    """Write threshold-tuning metrics in the self-describing envelope format."""
    save_json(
        path,
        {"defect_types": list(defect_types), "metrics": metrics},
    )


def unwrap_results(loaded):
    """Normalize an inference results object to ``(defect_types, items)``.

    Accepts both:
      - the new envelope: ``{"defect_types": [...], "items": [...]}``
      - the legacy list-only format: ``[{...}, {...}, ...]`` — in this case
        ``defect_types`` is inferred from ``items[0]["predictions"].keys()``.
    """
    if isinstance(loaded, dict) and "items" in loaded:
        items = loaded["items"]
        defect_types = list(loaded.get("defect_types") or [])
        if not defect_types and items:
            defect_types = list(items[0].get("predictions", {}).keys())
        return defect_types, items

    items = loaded
    defect_types = list(items[0].get("predictions", {}).keys()) if items else []
    return defect_types, items


def unwrap_threshold_metrics(loaded):
    """Normalize a threshold-metrics object to ``(defect_types, metrics)``.

    Accepts both:
      - the new envelope: ``{"defect_types": [...], "metrics": {...}}``
      - the legacy "metrics-only" format: ``{defect: {threshold: {...}}}`` —
        in this case ``defect_types`` is inferred from the top-level keys.
    """
    if isinstance(loaded, dict) and "metrics" in loaded:
        metrics = loaded["metrics"]
        defect_types = list(loaded.get("defect_types") or list(metrics.keys()))
        return defect_types, metrics

    return list(loaded.keys()), loaded


def default_results_path(root_dir, method, variant):
    """Conventional path for a runner's output JSON file.

    e.g. ``default_results_path(ROOT, "nli", "improved")`` ->
    ``<root>/results/nli/improved/results_nli_improved.json``.
    """
    return os.path.join(
        root_dir, "results", method, variant, f"results_{method}_{variant}.json"
    )
