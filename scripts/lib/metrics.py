"""Evaluation metrics and reporting helpers.

The reporting helpers (``print_evaluation``, ``print_comparison``) accept
result objects in either the new envelope format or the legacy list format
and discover the defect names from the data itself — no need to keep a
constant in sync with the experiment.
"""

from . import io as _io


def _entailment_predicate(item, defect):
    """Default rule: positive when stored label is ENTAILMENT."""
    return item["predictions"][defect]["label"] == "ENTAILMENT"


def compute_metrics(items, defect_type, *, predicate=None):
    """Compute precision, recall, F1 (and counts) for a single defect.

    By default uses the ENTAILMENT label rule used by ``run_nli`` /
    ``run_zeroshot``. Pass ``predicate(item, defect) -> bool`` for raw-score
    threshold sweeps (see ``evaluate_thresholds``).
    """
    pred = predicate or _entailment_predicate
    tp = fp = fn = tn = 0

    for item in items:
        actual = defect_type in item["ground_truth"]
        predicted = pred(item, defect_type)

        if actual and predicted:
            tp += 1
        elif not actual and predicted:
            fp += 1
        elif actual and not predicted:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }


def macro_average(per_defect_metrics, keys=("precision", "recall", "f1")):
    """Average each metric across defects."""
    n = len(per_defect_metrics)
    return {
        k: round(sum(m[k] for m in per_defect_metrics.values()) / n, 4)
        for k in keys
    }


def evaluate_thresholds(scored_items, defect_types, thresholds):
    """For each (defect, threshold) compute metrics from raw zero-shot scores.

    ``scored_items`` must contain ``scores`` (as produced by
    ``inference.collect_zeroshot_scores``).
    """
    out = {}
    for defect in defect_types:
        out[defect] = {}
        for t in thresholds:
            out[defect][str(t)] = compute_metrics(
                scored_items,
                defect,
                predicate=lambda item, d, t=t: item["scores"][d] >= t,
            )
    return out


def print_evaluation(loaded, defect_types=None, *, header=None):
    """Print per-defect P/R/F1 plus macro average. Returns the per-defect metrics.

    ``loaded`` is what ``io.load_results`` returns (envelope dict or legacy
    list). When ``defect_types`` is omitted it is taken from the loaded
    object (or inferred from the items).
    """
    discovered, items = _io.unwrap_results(loaded)
    defect_types = defect_types or discovered

    if header:
        print(header)
        print(f"Loaded {len(items)} results.\n")
    print("=" * 50)

    all_metrics = {}
    for defect in defect_types:
        m = compute_metrics(items, defect)
        all_metrics[defect] = m
        print(f"Defect: {defect}")
        print(f"  Precision: {m['precision']}")
        print(f"  Recall:    {m['recall']}")
        print(f"  F1:        {m['f1']}")
        print(f"  (TP={m['tp']}  FP={m['fp']}  FN={m['fn']}  TN={m['tn']})")
        print("-" * 50)

    macro = macro_average(all_metrics)
    print("MACRO AVERAGE")
    print(f"  Precision: {macro['precision']}")
    print(f"  Recall:    {macro['recall']}")
    print(f"  F1:        {macro['f1']}")
    print("=" * 50)

    return all_metrics


def fmt_diff(diff):
    """Format a numeric difference with explicit sign (used by comparisons)."""
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.4f}"


def print_comparison(baseline_loaded, improved_loaded, defect_types=None,
                     baseline_label="Baseline", improved_label="Improved"):
    """Print a side-by-side comparison of two result sets.

    Both arguments are what ``io.load_results`` returns. Defect types are
    discovered from the baseline by default; pass ``defect_types`` to
    override (or to restrict the comparison to a subset).
    """
    bm_defects, bm_items = _io.unwrap_results(baseline_loaded)
    im_defects, im_items = _io.unwrap_results(improved_loaded)

    if defect_types is None:
        defect_types = bm_defects or im_defects
        if bm_defects and im_defects and set(bm_defects) != set(im_defects):
            print(f"⚠ defect_types differ: baseline={bm_defects} improved={im_defects}; "
                  f"comparing on baseline's set.")

    bm_per = {d: compute_metrics(bm_items, d) for d in defect_types}
    im_per = {d: compute_metrics(im_items, d) for d in defect_types}

    for defect in defect_types:
        bm, im = bm_per[defect], im_per[defect]
        print(f"=== {defect.upper()} ===")
        for metric in ("precision", "recall", "f1"):
            label = "F1" if metric == "f1" else metric.capitalize()
            diff = im[metric] - bm[metric]
            print(f"  {baseline_label} {label}:  {bm[metric]}")
            print(f"  {improved_label} {label}:  {im[metric]}")
            print(f"  Difference:     {fmt_diff(diff)}")
            print()

    bm_macro = macro_average(bm_per)
    im_macro = macro_average(im_per)
    print("=== MACRO AVERAGE ===")
    for metric in ("precision", "recall", "f1"):
        label = "F1" if metric == "f1" else metric.capitalize()
        diff = im_macro[metric] - bm_macro[metric]
        print(f"  {baseline_label} {label}:  {bm_macro[metric]}")
        print(f"  {improved_label} {label}:  {im_macro[metric]}")
        print(f"  Difference:     {fmt_diff(diff)}")
        print()
