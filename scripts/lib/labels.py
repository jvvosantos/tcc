"""PocketRE — Label verbalization registry.

Each entry is a ``LabelSet`` — the single source of truth for an experiment.
It bundles every parameter that can vary between experiments:

- ``dataset``    — path to the labeled dataset, relative to the project root
                   (e.g. ``"data/dataset_v2.json"``).
- ``defects``    — mapping defect name -> natural-language hypothesis the
                   NLI / zero-shot model checks against the requirement.
- ``thresholds`` — per-defect decision threshold. NLI ignores them (it
                   uses argmax over ENTAILMENT/NEUTRAL/CONTRADICTION);
                   zero-shot predicts ENTAILMENT when the entailment
                   score is strictly above the defect's threshold.

The defect names are defined per ``LabelSet`` (no global constant). The
runners persist them in the result JSON under ``defect_types`` so that
evaluation scripts pick them up automatically.

How to test a new label variant
-------------------------------
1. Add a new ``LabelSet`` at the bottom of this file with all three fields.
2. Register it in ``LABEL_SETS`` so it can be picked by name from the CLI.
3. Run any of the generic runners pointing at it, e.g.::

       python scripts/run_nli.py --labels concrete_v3
       python scripts/run_zeroshot.py --labels concrete_v3
       python scripts/evaluate.py results/nli/concrete_v3/results_nli_concrete_v3.json

No other files need to be touched. All variable configuration lives here.

Background: see @ai/MEMORY.md § "Defect hypotheses (label verbalization)".
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LabelSet:
    """Single source of truth for one experiment variant.

    Attributes
    ----------
    dataset:
        Path to the labeled requirements file, relative to the project root.
    defects:
        Mapping from defect name to the NLI hypothesis text.
    thresholds:
        Per-defect decision threshold for zero-shot classification.
        NLI runners ignore this (they use the model's argmax label directly).
    """

    dataset: str
    defects: dict
    thresholds: dict


BASELINE = LabelSet(
    dataset="data/dataset.json",
    defects={
        "ambiguous": "This requirement contains vague or unclear terms that can be interpreted in multiple ways.",
        "non_measurable": "This requirement cannot be objectively measured or tested.",
        "optional": "This requirement includes optional or non-mandatory behavior.",
    },
    thresholds={
        "ambiguous": 0.5,
        "non_measurable": 0.5,
        "optional": 0.5,
    },
)


IMPROVED = LabelSet(
    dataset="data/dataset.json",
    defects={
        "ambiguous": (
            "This requirement uses vague or subjective words such as clear, intuitive, "
            "fast, good, or efficient that can be interpreted differently by different people."
        ),
        "non_measurable": (
            "This requirement does not define measurable acceptance criteria such as "
            "time limits, quantities, percentages, thresholds, or objective constraints."
        ),
        "optional": (
            "This requirement uses optional language such as may, might, could, "
            "optionally, if necessary, or if appropriate."
        ),
    },
    thresholds={
        "ambiguous": 0.5,
        "non_measurable": 0.5,
        "optional": 0.5,
    },
)


IMPROVED_V2 = LabelSet(
    dataset="data/dataset.json",
    defects={
        "ambiguous": (
            "This requirement is ambiguous because it can be interpreted in multiple ways, "
            "has unclear references, or does not clearly specify what the system must do."
        ),
        "non_measurable": (
            "This requirement contains vague quality terms such as quickly, fast, good, "
            "large, easy, reliable, adequate, professional, efficient, user-friendly, "
            "or intuitive, without objective measurable criteria."
        ),
        "optional": (
            "This requirement is optional only if it uses explicit optional terms such as "
            "may, might, could, optionally, if necessary, or if appropriate. "
            "The word should alone is not enough."
        ),
    },
    thresholds={
        "ambiguous": 0.75,
        "non_measurable": 0.30,
        "optional": 0.70,
    },
)


IMPROVED_V3 = LabelSet(
    dataset="data/dataset_v2.json",
    defects={
        "vague": (
            "This requirement is vague because it uses subjective or imprecise language "
            "such as fast, quick, good, efficient, reliable, user-friendly, intuitive, "
            "adequate, or large, and does not clearly define exact behavior or measurable criteria."
        ),
        "optional": (
            "This requirement is optional only if it uses explicit optional terms such as "
            "may, might, could, optionally, if necessary, or if appropriate. "
            "The word should alone is not enough to indicate optionality."
        ),
    },
    thresholds={
        "vague": 0.45,
        "optional": 0.70,
    },
)


IMPROVED_V4 = LabelSet(
    dataset="data/dataset_v2.json",
    defects={
        "vague": (
            "This requirement is vague ONLY if it explicitly contains subjective words such as "
            "fast, quick, good, efficient, reliable, user-friendly, intuitive, adequate, or large. "
            "If none of these words appear, it is not vague."
        ),
        "optional": (
            "This requirement is optional ONLY if it explicitly contains terms such as "
            "may, might, could, optionally, if necessary, or if appropriate. "
            "The words must or shall indicate that it is NOT optional."
        ),
    },
    thresholds={
        "vague": 0.65,
        "optional": 0.75,
    },
)

IMPROVED_V5 = LabelSet(
    dataset="data/dataset_v2.json",
    defects={
        "vague": (
            "This requirement is vague ONLY if it explicitly contains subjective words such as "
            "fast, quick, good, efficient, reliable, user-friendly, intuitive, adequate, or large. "
            "If none of these words appear, it is not vague."
        ),
        "optional": (
            "This requirement is optional ONLY if it explicitly contains terms such as "
            "may, might, could, optionally, if necessary, or if appropriate. "
            "The words must or shall indicate that it is NOT optional."
        ),
    },
    thresholds={
        "vague": 0.4,
        "optional": 0.3,
    },
)


LABEL_SETS = {
    "baseline": BASELINE,
    "improved": IMPROVED,
    "improved_v2": IMPROVED_V2,
    "improved_v3": IMPROVED_V3,
    "improved_v4": IMPROVED_V4,
    "improved_v5": IMPROVED_V5,
}


def get(name):
    """Look up a label set by name, with a clear error if it does not exist."""
    if name not in LABEL_SETS:
        available = ", ".join(sorted(LABEL_SETS))
        raise KeyError(f"Unknown label set '{name}'. Available: {available}")
    return LABEL_SETS[name]
