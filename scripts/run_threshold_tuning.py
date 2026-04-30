"""PocketRE — Generic threshold tuning runner.

Runs zero-shot inference once, stores the raw entailment score per defect,
then evaluates several decision thresholds to find the best F1.

Outputs land under ``results/zeroshot/threshold_tuning_<labels>/`` unless
``--out-dir`` is provided.

Example
-------
    python scripts/run_threshold_tuning.py --labels improved
    python scripts/run_threshold_tuning.py --labels concrete_v3 \
        --thresholds 0.2 0.3 0.4 0.5 0.6 0.7 0.8
"""

import argparse
import os
import sys

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(ROOT_DIR))

from scripts.lib import inference, io, labels, metrics  # noqa: E402

DATASET_PATH = os.path.join(ROOT_DIR, "data", "dataset_v2.json")
DEFAULT_MODEL = "facebook/bart-large-mnli"
DEFAULT_THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7]


def parse_args():
    parser = argparse.ArgumentParser(description="Sweep zero-shot decision thresholds.")
    parser.add_argument(
        "--labels",
        required=True,
        help=f"Label set name. Available: {sorted(labels.LABEL_SETS)}",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="HF model name.")
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        default=DEFAULT_THRESHOLDS,
        help="List of thresholds to evaluate (default: 0.3 0.4 0.5 0.6 0.7).",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Defaults to results/zeroshot/threshold_tuning_<labels>/.",
    )
    return parser.parse_args()


def write_summary(metrics_dict, defect_types, thresholds, path, model_name, labels_name):
    lines = [
        "PocketRE — Threshold Tuning Summary",
        f"Model:   {model_name}",
        f"Labels:  {labels_name}",
        f"Thresholds tested: {thresholds}",
        "=" * 60,
        "",
    ]

    for defect in defect_types:
        lines.append(f"Defect: {defect}")
        lines.append("-" * 40)

        best_t, best_f1 = None, -1.0
        for t in thresholds:
            m = metrics_dict[defect][str(t)]
            if m["f1"] > best_f1:
                best_f1 = m["f1"]
                best_t = t
            lines.append(
                f"  t={t:.1f}  P={m['precision']:.4f}  R={m['recall']:.4f}  "
                f"F1={m['f1']:.4f}  (TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']})"
            )

        lines.append(f"  >>> Best threshold: {best_t} (F1={best_f1:.4f})")
        lines.append("")

    lines.append("=" * 60)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    args = parse_args()

    label_set = labels.get(args.labels)
    defect_types = list(label_set.defects.keys())
    out_dir = args.out_dir or os.path.join(
        ROOT_DIR, "results", "zeroshot", f"threshold_tuning_{args.labels}"
    )

    dataset = io.load_dataset(DATASET_PATH)
    scored_items = inference.collect_zeroshot_scores(args.model, dataset, label_set)

    metrics_dict = metrics.evaluate_thresholds(
        scored_items, defect_types, args.thresholds
    )

    metrics_path = os.path.join(out_dir, "threshold_metrics.json")
    io.save_threshold_metrics(metrics_path, defect_types, metrics_dict)
    print(f"\nMetrics saved to {metrics_path}")

    summary_path = os.path.join(out_dir, "threshold_summary.txt")
    write_summary(
        metrics_dict, defect_types, args.thresholds,
        summary_path, args.model, args.labels,
    )
    print(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    main()
