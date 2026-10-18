"""Canonical crop classifier training with multi-model benchmarking."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, Tuple

import matplotlib

matplotlib.use("Agg")
import joblib
import numpy as np
import pandas as pd
from scipy.stats import randint, uniform
from sklearn.base import clone
from sklearn.metrics import classification_report
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.preprocessing import LabelEncoder

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.evaluation.metrics import (  # noqa: E402
    classification_scores,
    confusion_matrix_png,
    model_comparison_bar,
)
from src.models.crop_models import crop_classifier_factories  # noqa: E402
from src.preprocessing.crop_preprocessor import (  # noqa: E402
    build_crop_preprocessor,
    load_balanced_baseline_crop_dataframe,
)
from src.utils.paths import load_config, project_root  # noqa: E402


def _maybe_subsample_svm(
    X: pd.DataFrame, y: pd.Series, max_samples: int
) -> Tuple[pd.DataFrame, pd.Series]:
    """Stratified subsample for expensive kernel SVM training."""
    if len(X) <= max_samples:
        return X, y
    X_s, _, y_s, _ = train_test_split(
        X,
        y,
        train_size=max_samples,
        stratify=y,
        random_state=42,
    )
    return X_s, y_s


def _tune_rf(
    pipe: Any,
    X: Any,
    y: Any,
    cv: Any,
    n_iter: int,
    random_state: int,
    n_jobs: int = -1,
) -> Tuple[Any, Dict[str, Any]]:
    param_dist = {
        "classifier__n_estimators": randint(80, 220),
        "classifier__max_depth": [None, 10, 20, 30, 40],
        "classifier__min_samples_split": randint(2, 12),
    }
    search = RandomizedSearchCV(
        estimator=pipe,
        param_distributions=param_dist,
        n_iter=n_iter,
        scoring="f1_macro",
        cv=cv,
        n_jobs=n_jobs,
        random_state=random_state,
        refit=True,
        verbose=1,
    )
    search.fit(X, y)
    best_params = {k.replace("classifier__", ""): v for k, v in search.best_params_.items()}
    return search.best_estimator_, {"best_params": best_params}


def _tune_xgb(
    pipe: Any,
    X: Any,
    y: Any,
    cv: Any,
    n_iter: int,
    random_state: int,
    n_jobs: int = -1,
) -> Tuple[Any, Dict[str, Any]]:
    param_dist = {
        "classifier__n_estimators": randint(80, 200),
        "classifier__learning_rate": uniform(0.03, 0.17),
        "classifier__max_depth": randint(3, 11),
        "classifier__subsample": uniform(0.7, 0.29),
    }
    search = RandomizedSearchCV(
        estimator=pipe,
        param_distributions=param_dist,
        n_iter=n_iter,
        scoring="f1_macro",
        cv=cv,
        n_jobs=n_jobs,
        random_state=random_state,
        refit=True,
        verbose=1,
    )
    search.fit(X, y)
    best_params = {k.replace("classifier__", ""): float(v) if isinstance(v, (np.floating, float)) else int(v) for k, v in search.best_params_.items()}
    return search.best_estimator_, {"best_params": best_params}


def main() -> None:
    """Train, compare, persist crop classifiers (Experiment 1 — balanced baseline)."""
    cfg = load_config()
    root = project_root()
    crop_cfg = cfg["models"]["crop"]
    mode = str(crop_cfg.get("training_mode", "balanced_only"))
    if mode == "merged_smote":
        print(
            "models.crop.training_mode is 'merged_smote'. "
            "Experiment 1 (production) expects 'balanced_only' in config.yaml.\n"
            "Run Experiment 2 with: python src/training/train_crop_experiment.py"
        )
        sys.exit(1)
    if mode != "balanced_only":
        raise ValueError(
            f"Unknown models.crop.training_mode {mode!r}; use 'balanced_only' or 'merged_smote'."
        )

    raw_dir = root / cfg["paths"]["data_raw"]
    art_models = root / cfg["paths"]["artifacts_models"]
    art_reports = root / cfg["paths"]["artifacts_reports"]
    art_models.mkdir(parents=True, exist_ok=True)
    art_reports.mkdir(parents=True, exist_ok=True)

    tcfg = cfg["training"]
    nj = int(tcfg.get("parallel_n_jobs", -1))
    cv = StratifiedKFold(n_splits=int(tcfg["cv_folds"]), shuffle=True, random_state=int(tcfg["random_state"]))

    X, y_str = load_balanced_baseline_crop_dataframe(raw_dir)
    le = LabelEncoder()
    y_encoded = le.fit_transform(np.asarray(y_str))
    # Single encoding for all splits, CV, and scoring (no second encoder).
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=float(tcfg["test_size"]),
        random_state=int(tcfg["random_state"]),
        stratify=y_encoded,
    )
    y_train_arr = np.asarray(y_train).astype(int).ravel()
    y_test_arr = np.asarray(y_test).astype(int).ravel()

    factories = crop_classifier_factories()
    results_meta: Dict[str, Any] = {}
    f1_scores_for_chart: Dict[str, float] = {}

    for name, factory in factories.items():
        print(f"\n=== Training {name} ===")
        pre = build_crop_preprocessor()
        pipe = factory(pre)

        X_tr, y_tr = X_train, y_train_arr
        if name == "SVM":
            max_s = int(tcfg.get("svm_max_samples", 12000))
            y_train_series = pd.Series(y_train_arr, index=X_train.index)
            X_tr, y_tr_series = _maybe_subsample_svm(X_train, y_train_series, max_s)
            y_tr = np.asarray(y_tr_series).astype(int).ravel()

        if name in ("RandomForest", "XGBoost"):
            n_iter = int(tcfg["search_n_iter_rf"] if name == "RandomForest" else tcfg["search_n_iter_xgb"])
            if name == "RandomForest":
                best_pipe, extra = _tune_rf(
                    pipe, X_tr, y_tr, cv, n_iter, int(tcfg["random_state"]), n_jobs=nj
                )
            else:
                best_pipe, extra = _tune_xgb(
                    pipe, X_tr, y_tr, cv, n_iter, int(tcfg["random_state"]), n_jobs=nj
                )
            cv_f1 = cross_val_score(
                clone(best_pipe), X_train, y_train_arr, cv=cv, scoring="f1_macro", n_jobs=nj
            )
            pipe_fit = best_pipe
            meta_extra = extra
        else:
            cv_f1 = cross_val_score(pipe, X_tr, y_tr, cv=cv, scoring="f1_macro", n_jobs=nj)
            pipe_fit = clone(pipe)
            pipe_fit.fit(X_train, y_train_arr)
            meta_extra = {"best_params": {}}

        y_pred = np.asarray(pipe_fit.predict(X_test), dtype=int).ravel()
        proba = pipe_fit.predict_proba(X_test) if hasattr(pipe_fit, "predict_proba") else None
        scores = classification_scores(
            y_test_arr,
            y_pred,
            proba,
            labels=np.arange(len(le.classes_)),
        )

        results_meta[name] = {
            **scores,
            "cv_f1_mean": float(np.mean(cv_f1)),
            "cv_f1_std": float(np.std(cv_f1)),
            **meta_extra,
        }
        f1_scores_for_chart[name] = scores["f1_macro"]
        print(
            f"{name}: acc={scores['accuracy']:.4f} f1_w={scores['f1_weighted']:.4f} "
            f"f1_macro={scores['f1_macro']:.4f} "
            f"cv_f1={np.mean(cv_f1):.4f}+/-{np.std(cv_f1):.4f}"
        )

        acc_f = float(scores["accuracy"])
        f1w_f = float(scores["f1_weighted"])
        f1m_f = float(scores["f1_macro"])
        # Accuracy and weighted F1 both reflect support-weighted correctness;
        # a large gap here usually means a bug (e.g. misaligned y vs y_pred).
        gap_w = abs(acc_f - f1w_f)
        if gap_w > 0.02:
            print(
                f"[WARN] {name}: |accuracy - F1_weighted| = {gap_w:.4f} "
                "(unexpected if labels are aligned row-wise)."
            )
        gap_m = abs(acc_f - f1m_f)
        if gap_m > 0.25:
            print(
                f"[INFO] {name}: |accuracy - F1_macro| = {gap_m:.4f} — common when "
                "macro-F1 is dominated by low-support classes; trust F1_weighted vs "
                "accuracy for overall fit quality on imbalanced data."
            )

    best_name = max(f1_scores_for_chart, key=f1_scores_for_chart.get)
    print(f"\nBest model by F1-macro on hold-out: {best_name}")

    # Refit best architecture on full data for production artifact
    pre_best = build_crop_preprocessor()
    best_pipe_template = factories[best_name](pre_best)
    if best_name in ("RandomForest", "XGBoost"):
        tuned, _ = (
            _tune_rf(
                best_pipe_template,
                X,
                y_encoded,
                cv,
                int(tcfg["search_n_iter_rf"]),
                int(tcfg["random_state"]),
                n_jobs=nj,
            )
            if best_name == "RandomForest"
            else _tune_xgb(
                best_pipe_template,
                X,
                y_encoded,
                cv,
                int(tcfg["search_n_iter_xgb"]),
                int(tcfg["random_state"]),
                n_jobs=nj,
            )
        )
        final_estimator = tuned
    else:
        X_full, y_full = X, y_encoded
        if best_name == "SVM":
            y_idx = pd.Series(y_encoded, index=X.index)
            X_full, y_series = _maybe_subsample_svm(
                X, y_idx, int(tcfg.get("svm_max_samples", 12000))
            )
            y_full = np.asarray(y_series).astype(int).ravel()
        final_estimator = clone(best_pipe_template)
        final_estimator.fit(X_full, y_full)

    y_hat_full = np.asarray(final_estimator.predict(X_test), dtype=int).ravel()
    _ = (
        final_estimator.predict_proba(X_test)
        if hasattr(final_estimator, "predict_proba")
        else None
    )
    labels_idx = np.arange(len(le.classes_))
    report = classification_report(
        y_test_arr,
        y_hat_full,
        labels=labels_idx,
        target_names=list(le.classes_),
        output_dict=True,
        zero_division=0,
    )

    holdout_scores = classification_scores(
        y_test_arr,
        y_hat_full,
        final_estimator.predict_proba(X_test)
        if hasattr(final_estimator, "predict_proba")
        else None,
        labels=labels_idx,
    )
    assert float(holdout_scores["accuracy"]) > 0.98, (
        f"Balanced baseline hold-out accuracy {holdout_scores['accuracy']:.4f} "
        "expected > 0.98 (check data / model configuration)."
    )
    assert float(holdout_scores["f1_macro"]) > 0.98, (
        f"Balanced baseline hold-out F1 macro {holdout_scores['f1_macro']:.4f} "
        "expected > 0.98 (check data / model configuration)."
    )

    crop_meta = {
        "experiment": "balanced_baseline",
        "training_mode": "balanced_only",
        "data_source": "Crop_recommendation.csv_only",
        "best_model": best_name,
        "best_f1_macro": float(f1_scores_for_chart[best_name]),
        "holdout_metrics_best_pipeline": holdout_scores,
        "training_date": date.today().isoformat(),
        "models": results_meta,
        "classification_report": report,
    }

    meta_path = root / cfg["models"]["crop"]["metadata_path"]
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(crop_meta, fh, indent=2, default=str)

    artifact = {"pipeline": final_estimator, "label_encoder": le}
    model_path = root / cfg["models"]["crop"]["artifact_path"]
    joblib.dump(artifact, model_path)

    model_comparison_bar(
        list(f1_scores_for_chart.keys()),
        list(f1_scores_for_chart.values()),
        "F1 macro (hold-out test)",
        "Crop classifier comparison",
        str(art_reports / "crop_model_comparison.png"),
    )
    confusion_matrix_png(
        y_test_arr,
        y_hat_full,
        list(le.classes_),
        str(art_reports / "crop_confusion_matrix.png"),
    )

    print("\nSaved:")
    print(f"  Model: {model_path}")
    print(f"  Metadata: {meta_path}")
    print(f"  Reports: {art_reports}")


if __name__ == "__main__":
    main()
