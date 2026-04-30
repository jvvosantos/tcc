"""Inference helpers wrapping Hugging Face pipelines.

All public functions accept a ``LabelSet`` (see ``scripts/lib/labels.py``)
so that defect hypotheses and per-defect decision thresholds travel
together.

Standard PocketRE result format produced by ``run_nli`` / ``run_zeroshot``::

    {
        "requirement": str,
        "ground_truth": list[str],
        "predictions": {defect_name: {"label": str, "score": float}},
    }

``collect_zeroshot_scores`` is the exception used by threshold tuning:
it stores the raw entailment ``score`` per defect so different thresholds
can be evaluated downstream without re-running inference.
"""

from transformers import pipeline


def _classify_nli(nli_pipeline, requirement, defects):
    predictions = {}
    for defect_name, hypothesis in defects.items():
        result = nli_pipeline(
            {"text": requirement, "text_pair": hypothesis},
            top_k=None,
        )
        best = max(result, key=lambda x: x["score"])
        predictions[defect_name] = {
            "label": best["label"],
            "score": round(best["score"], 4),
        }
    return predictions


def _classify_zeroshot(classifier, requirement, defects, thresholds):
    hypotheses = list(defects.values())
    defect_names = list(defects.keys())

    result = classifier(
        requirement,
        candidate_labels=hypotheses,
        hypothesis_template="{}",
        multi_label=True,
    )

    predictions = {}
    for hypothesis, score in zip(result["labels"], result["scores"]):
        defect_name = defect_names[hypotheses.index(hypothesis)]
        threshold = thresholds[defect_name]
        label = "ENTAILMENT" if score > threshold else "NEUTRAL"
        predictions[defect_name] = {
            "label": label,
            "score": round(score, 4),
        }
    return predictions


def _iterate_dataset(dataset, classify_fn):
    results = []
    n = len(dataset)
    for i, item in enumerate(dataset):
        req = item["requirement"]
        print(f"  [{i + 1}/{n}] {req[:80]}...")
        results.append({
            "requirement": req,
            "ground_truth": item["defects"],
            "predictions": classify_fn(req),
        })
    return results


def run_nli(model_name, dataset, label_set):
    """Run NLI inference for every (requirement, defect) pair.

    NLI uses the model's argmax label directly; ``label_set.thresholds`` is
    ignored.
    """
    print(f"Loading model: {model_name}")
    nli = pipeline("text-classification", model=model_name)
    print(f"Loaded {len(dataset)} requirements from dataset.")
    return _iterate_dataset(
        dataset, lambda req: _classify_nli(nli, req, label_set.defects)
    )


def run_zeroshot(model_name, dataset, label_set):
    """Run zero-shot classification with per-defect thresholds from the label set."""
    print(f"Loading model: {model_name}")
    classifier = pipeline("zero-shot-classification", model=model_name)
    print(f"Loaded {len(dataset)} requirements from dataset.")
    return _iterate_dataset(
        dataset,
        lambda req: _classify_zeroshot(
            classifier, req, label_set.defects, label_set.thresholds
        ),
    )


def collect_zeroshot_scores(model_name, dataset, label_set):
    """Run zero-shot and keep only raw scores per defect (no thresholding).

    Returned items use the key ``scores`` instead of ``predictions`` so that
    threshold tuning can sweep multiple cutoffs without re-running inference.
    ``label_set.thresholds`` is ignored here.
    """
    print(f"Loading model: {model_name}")
    classifier = pipeline("zero-shot-classification", model=model_name)
    print(f"Loaded {len(dataset)} requirements from dataset.\n")

    hypotheses = list(label_set.defects.values())
    defect_names = list(label_set.defects.keys())
    scored_items = []

    for i, item in enumerate(dataset):
        req = item["requirement"]
        print(f"  [{i + 1}/{len(dataset)}] {req[:80]}...")

        result = classifier(
            req,
            candidate_labels=hypotheses,
            hypothesis_template="{}",
            multi_label=True,
        )

        scores = {}
        for hypothesis, score in zip(result["labels"], result["scores"]):
            name = defect_names[hypotheses.index(hypothesis)]
            scores[name] = round(score, 4)

        scored_items.append({
            "requirement": req,
            "ground_truth": item["defects"],
            "scores": scores,
        })

    return scored_items
