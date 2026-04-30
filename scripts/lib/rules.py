"""Rule-based defect detection (lexical baseline).

Pure-Python alternative to NLI / zero-shot. For each defect, a list of
trigger terms (single words or short phrases) is provided in
``LabelSet.terms``; a requirement is flagged for that defect when **at least
one** term matches the requirement text using case-insensitive whole-word
regex matching.

This baseline exists to answer a specific question for the TCC: how much of
the BART zero-shot signal is genuine entailment versus lexical pattern
matching? If a 30-line regex can match (or beat) the F1 of a 400M-parameter
model, that is a strong empirical statement about the task.

Output format mirrors ``inference.run_nli`` / ``inference.run_zeroshot`` so
that ``evaluate.py``, ``compare_experiments.py`` and the rest of the
pipeline work unchanged. Each item produces::

    {
        "requirement": str,
        "ground_truth": list[str],
        "predictions": {
            defect_name: {
                "label": "ENTAILMENT" | "NEUTRAL",
                "score": float,             # matched_count / total_terms
                "matched_terms": list[str],
            },
            ...
        },
    }

``score`` is a normalized match count (0.0 = no match, 1.0 = every term
matched) so that downstream threshold tuning is possible if desired (e.g.
require at least N matches to fire), without changing the format.
"""

import re


def _compile_term(term):
    """Compile a single term into a case-insensitive whole-word pattern.

    Multi-word phrases (``"if necessary"``) are escaped and wrapped with
    ``\\b`` boundaries so that they only match as standalone occurrences:
    ``"may"`` does not match ``"maybe"`` or ``"Mayor"``.
    """
    return re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)


def _build_term_index(terms):
    """Pre-compile every defect's term list once for the whole run."""
    return {
        defect: [(term, _compile_term(term)) for term in defect_terms]
        for defect, defect_terms in terms.items()
    }


def _classify_rules(requirement, term_index):
    predictions = {}
    for defect, compiled_terms in term_index.items():
        matched = [term for term, pattern in compiled_terms if pattern.search(requirement)]
        total = len(compiled_terms) or 1
        score = round(len(matched) / total, 4)
        predictions[defect] = {
            "label": "ENTAILMENT" if matched else "NEUTRAL",
            "score": score,
            "matched_terms": matched,
        }
    return predictions


def run_rules(dataset, label_set):
    """Apply rule-based lexical matching to every requirement in ``dataset``.

    ``label_set.terms`` must be set (a mapping ``defect -> list[str]``);
    raises ``ValueError`` otherwise. ``label_set.defects`` /
    ``label_set.thresholds`` are not used by this method.
    """
    if not getattr(label_set, "terms", None):
        raise ValueError(
            "Rule-based runner requires LabelSet.terms to be defined "
            "(mapping defect_name -> list of trigger terms)."
        )

    term_index = _build_term_index(label_set.terms)
    print(f"Loaded {len(dataset)} requirements from dataset.")
    print(f"Defects: {list(label_set.terms.keys())}")
    for defect, defect_terms in label_set.terms.items():
        print(f"  {defect}: {len(defect_terms)} terms")
    print()

    results = []
    n = len(dataset)
    for i, item in enumerate(dataset):
        req = item["requirement"]
        print(f"  [{i + 1}/{n}] {req[:80]}...")
        results.append({
            "requirement": req,
            "ground_truth": item["defects"],
            "predictions": _classify_rules(req, term_index),
        })
    return results
