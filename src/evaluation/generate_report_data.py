"""Compare Experiment 1 (balanced baseline) vs Experiment 2 (merged + SMOTE) metrics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.utils.paths import load_config, project_root  # noqa: E402

MODEL_ORDER = [
    "RandomForest",
    "XGBoost",
    "SVM",
    "KNN",
    "GradientBoosting",
]


def main() -> None:
    cfg = load_config()
    root = project_root()
    exp1_path = root / cfg["models"]["crop"]["metadata_path"]
    exp2_path = root / cfg["models"]["crop"]["experiment_metadata_path"]

    if not exp1_path.exists():
        raise FileNotFoundError(
            f"Experiment 1 metadata missing: {exp1_path}. Run: python src/training/train_crop.py"
        )
    if not exp2_path.exists():
        raise FileNotFoundError(
            f"Experiment 2 metadata missing: {exp2_path}. "
            "Run: python src/training/train_crop_experiment.py"
        )

    with open(exp1_path, "r", encoding="utf-8") as fh:
        exp1 = json.load(fh)
    with open(exp2_path, "r", encoding="utf-8") as fh:
        exp2 = json.load(fh)

    e1_models = exp1.get("models") or {}
    e2_smote = (exp2.get("smote_balanced_holdout") or {})

    rows = []
    for m in MODEL_ORDER:
        if m not in e1_models or m not in e2_smote:
            raise KeyError(
                f"Missing metrics for model {m!r} in exp1 and/or exp2 metadata."
            )
        rows.append(
            {
                "Model": m,
                "Exp1_Accuracy": float(e1_models[m]["accuracy"]),
                "Exp2_Accuracy": float(e2_smote[m]["accuracy"]),
                "Exp1_F1_macro": float(e1_models[m]["f1_macro"]),
                "Exp2_F1_macro": float(e2_smote[m]["f1_macro"]),
            }
        )

    df = pd.DataFrame(rows)
    out_csv = root / cfg["paths"]["artifacts_reports"] / "experiment_comparison.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    header = (
        f"| {'Model':<18} | {'Exp1 Accuracy':>14} | {'Exp2 Accuracy':>14} | "
        f"{'Exp1 F1':>10} | {'Exp2 F1':>10} |"
    )
    sep = (
        f"|{'-' * 20}|{'-' * 16}|{'-' * 16}|{'-' * 12}|{'-' * 12}|"
    )
    print("\nExperiment comparison (hold-out test set)\n")
    print(header)
    print(sep)
    for _, r in df.iterrows():
        print(
            f"| {r['Model']:<18} | {r['Exp1_Accuracy']:>14.4f} | {r['Exp2_Accuracy']:>14.4f} | "
            f"{r['Exp1_F1_macro']:>10.4f} | {r['Exp2_F1_macro']:>10.4f} |"
        )
    print(f"\nSaved: {out_csv}")


if __name__ == "__main__":
    main()
