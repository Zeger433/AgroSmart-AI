"""Experiment 2 — merged crop data: raw hold-out vs SMOTE + class-weighted training."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_sample_weight

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.evaluation.metrics import classification_scores  # noqa: E402
from src.models.crop_models import crop_classifier_factories  # noqa: E402
from src.preprocessing.crop_preprocessor import (  # noqa: E402
    build_crop_preprocessor,
    load_combined_crop_dataframe,
)
from src.training.train_crop import (  # noqa: E402
    _maybe_subsample_svm,
    _tune_rf,
    _tune_xgb,
)
from src.utils.paths import load_config, project_root  # noqa: E402


def _smote_k_neighbors(y: np.ndarray, requested: int = 3) -> int:
    """``k_neighbors`` must be ``<`` smallest class count in training labels."""
    _, counts = np.unique(y, return_counts=True)
    m = int(counts.min())
    return max(1, min(int(requested), m - 1))


def _sk_pipeline_to_imb_pipeline_with_smote(
    sk_pipeline: Pipeline,
    k_neighbors: int,
) -> ImbPipeline:
    """Insert ``SMOTE`` after all transform steps and before ``classifier``."""
    sm = SMOTE(random_state=42, k_neighbors=k_neighbors)
    steps_before: list[tuple[str, Any]] = []
    classifier = None
    for name, step in sk_pipeline.steps:
        if name == "classifier":
            classifier = clone(step)
        else:
            steps_before.append((name, clone(step)))
    if classifier is None:
        raise ValueError("Expected a final step named 'classifier'")
    imb_steps = steps_before + [("smote", sm)] + [("classifier", classifier)]
    return ImbPipeline(imb_steps)


def _gbc_balanced_fit(pipe: Pipeline, X: pd.DataFrame, y: np.ndarray) -> None:
    sw = compute_sample_weight("balanced", y)
    pipe.fit(X, y, classifier__sample_weight=sw)


def _fit_raw_merged_model(
    name: str,
    factory: Any,
    X_train: pd.DataFrame,
    y_train_arr: np.ndarray,
    X_test: pd.DataFrame,
    y_test_arr: np.ndarray,
    le: LabelEncoder,
    cv: StratifiedKFold,
    tcfg: Dict[str, Any],
    n_jobs: int,
) -> Tuple[Any, np.ndarray, Dict[str, Any]]:
    """Train on original (imbalanced) training rows; evaluate on ``X_test``."""
    pre = build_crop_preprocessor()
    pipe = factory(pre)

    X_tr, y_tr = X_train, y_train_arr
    if name == "SVM":
        max_s = int(tcfg.get("svm_max_samples", 12000))
        y_series = pd.Series(y_train_arr, index=X_train.index)
        X_tr, y_tr_series = _maybe_subsample_svm(X_train, y_series, max_s)
        y_tr = np.asarray(y_tr_series).astype(int).ravel()

    if name in ("RandomForest", "XGBoost"):
        n_iter = int(tcfg["search_n_iter_rf"] if name == "RandomForest" else tcfg["search_n_iter_xgb"])
        if name == "RandomForest":
            best_pipe, extra = _tune_rf(
                pipe, X_tr, y_tr, cv, n_iter, int(tcfg["random_state"]), n_jobs=n_jobs
            )
        else:
            best_pipe, extra = _tune_xgb(
                pipe, X_tr, y_tr, cv, n_iter, int(tcfg["random_state"]), n_jobs=n_jobs
            )
        cv_f1 = cross_val_score(
            clone(best_pipe), X_train, y_train_arr, cv=cv, scoring="f1_macro", n_jobs=n_jobs
        )
        pipe_fit = best_pipe
        meta_extra = {**extra, "cv_f1_mean": float(np.mean(cv_f1)), "cv_f1_std": float(np.std(cv_f1))}
    else:
        pipe_fit = clone(pipe)
        if name == "GradientBoosting":
            _gbc_balanced_fit(pipe_fit, X_train, y_train_arr)
        else:
            pipe_fit.fit(X_train, y_train_arr)
        cv_f1 = cross_val_score(
            clone(pipe), X_tr, y_tr, cv=cv, scoring="f1_macro", n_jobs=n_jobs
        )
        meta_extra = {
            "best_params": {},
            "cv_f1_mean": float(np.mean(cv_f1)),
            "cv_f1_std": float(np.std(cv_f1)),
        }

    y_pred = np.asarray(pipe_fit.predict(X_test), dtype=int).ravel()
    proba = pipe_fit.predict_proba(X_test) if hasattr(pipe_fit, "predict_proba") else None
    scores = classification_scores(
        y_test_arr,
        y_pred,
        proba,
        labels=np.arange(len(le.classes_)),
    )
    return pipe_fit, y_pred, {**scores, **meta_extra}


def _fit_smote_model(
    name: str,
    factory: Any,
    X_train: pd.DataFrame,
    y_train_arr: np.ndarray,
    X_test: pd.DataFrame,
    y_test_arr: np.ndarray,
    le: LabelEncoder,
    cv: StratifiedKFold,
    tcfg: Dict[str, Any],
    k_smote: int,
    n_jobs: int,
) -> Tuple[Any, np.ndarray, Dict[str, Any]]:
    """Train with ``SMOTE`` inside the pipeline (training folds only in CV)."""
    pre = build_crop_preprocessor()
    sk_base = factory(pre)
    imb_base = _sk_pipeline_to_imb_pipeline_with_smote(sk_base, k_smote)

    X_tr, y_tr = X_train, y_train_arr
    if name == "SVM":
        max_s = int(tcfg.get("svm_max_samples", 12000))
        y_series = pd.Series(y_train_arr, index=X_train.index)
        X_tr, y_tr_series = _maybe_subsample_svm(X_train, y_series, max_s)
        y_tr = np.asarray(y_tr_series).astype(int).ravel()

    if name in ("RandomForest", "XGBoost"):
        n_iter = int(tcfg["search_n_iter_rf"] if name == "RandomForest" else tcfg["search_n_iter_xgb"])
        if name == "RandomForest":
            best_pipe, extra = _tune_rf(
                imb_base, X_tr, y_tr, cv, n_iter, int(tcfg["random_state"]), n_jobs=n_jobs
            )
        else:
            best_pipe, extra = _tune_xgb(
                imb_base, X_tr, y_tr, cv, n_iter, int(tcfg["random_state"]), n_jobs=n_jobs
            )
        cv_f1 = cross_val_score(
            clone(best_pipe), X_train, y_train_arr, cv=cv, scoring="f1_macro", n_jobs=n_jobs
        )
        pipe_fit = best_pipe
        meta_extra = {**extra, "cv_f1_mean": float(np.mean(cv_f1)), "cv_f1_std": float(np.std(cv_f1))}
    else:
        pipe_fit = clone(imb_base)
        pipe_fit.fit(X_train, y_train_arr)
        cv_f1 = cross_val_score(
            clone(imb_base), X_tr, y_tr, cv=cv, scoring="f1_macro", n_jobs=n_jobs
        )
        meta_extra = {
            "best_params": {},
            "cv_f1_mean": float(np.mean(cv_f1)),
            "cv_f1_std": float(np.std(cv_f1)),
        }

    y_pred = np.asarray(pipe_fit.predict(X_test), dtype=int).ravel()
    proba = pipe_fit.predict_proba(X_test) if hasattr(pipe_fit, "predict_proba") else None
    scores = classification_scores(
        y_test_arr,
        y_pred,
        proba,
        labels=np.arange(len(le.classes_)),
    )
    return pipe_fit, y_pred, {**scores, **meta_extra}


def _plot_imbalance_comparison(
    model_names: list[str],
    raw_acc: list[float],
    smote_acc: list[float],
    raw_f1: list[float],
    smote_f1: list[float],
    out_path: Path,
) -> None:
    """Side-by-side raw merged vs SMOTE hold-out metrics for all models."""
    x = np.arange(len(model_names))
    w = 0.35
    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ax0.bar(x - w / 2, raw_acc, w, label="Raw merged (train)", color="#9cb9a4")
    ax0.bar(x + w / 2, smote_acc, w, label="SMOTE-balanced (train)", color="#1a3c2e")
    ax0.set_ylabel("Hold-out accuracy")
    ax0.set_title("Imbalance experiment — merged crop data")
    ax0.legend(loc="lower right")
    ax0.set_ylim(0.0, 1.05)
    ax0.grid(axis="y", alpha=0.3)

    ax1.bar(x - w / 2, raw_f1, w, label="Raw merged (train)", color="#9cb9a4")
    ax1.bar(x + w / 2, smote_f1, w, label="SMOTE-balanced (train)", color="#1a3c2e")
    ax1.set_ylabel("Hold-out F1 macro")
    ax1.set_xticks(x)
    ax1.set_xticklabels(model_names, rotation=20, ha="right")
    ax1.legend(loc="lower right")
    ax1.set_ylim(0.0, 1.05)
    ax1.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    cfg = load_config()
    root = project_root()
    raw_dir = root / cfg["paths"]["data_raw"]
    art_models = root / cfg["paths"]["artifacts_models"]
    art_reports = root / cfg["paths"]["artifacts_reports"]
    art_models.mkdir(parents=True, exist_ok=True)
    art_reports.mkdir(parents=True, exist_ok=True)

    tcfg = cfg["training"]
    nj = int(tcfg.get("parallel_n_jobs", -1))
    cv = StratifiedKFold(
        n_splits=int(tcfg["cv_folds"]),
        shuffle=True,
        random_state=int(tcfg["random_state"]),
    )

    print("Experiment 2: merged crop data (raw vs SMOTE + class weights)", flush=True)
    X, y_str = load_combined_crop_dataframe(raw_dir)
    le = LabelEncoder()
    y_encoded = le.fit_transform(np.asarray(y_str))
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=float(tcfg["test_size"]),
        random_state=int(tcfg["random_state"]),
        stratify=y_encoded,
    )
    y_train_arr = np.asarray(y_train).astype(int).ravel()
    y_test_arr = np.asarray(y_test).astype(int).ravel()
    k_smote = _smote_k_neighbors(y_train_arr, requested=3)

    factories = crop_classifier_factories(class_weight_balanced=True)
    raw_models: Dict[str, Dict[str, Any]] = {}
    smote_models: Dict[str, Dict[str, Any]] = {}
    model_order: list[str] = []
    y_hat_report: np.ndarray | None = None

    for name, factory in factories.items():
        model_order.append(name)
        print(f"\n=== Raw merged — {name} ===")
        _, _, raw_scores = _fit_raw_merged_model(
            name,
            factory,
            X_train,
            y_train_arr,
            X_test,
            y_test_arr,
            le,
            cv,
            tcfg,
            nj,
        )
        raw_models[name] = raw_scores
        print(
            f"{name}: acc={raw_scores['accuracy']:.4f} "
            f"f1_macro={raw_scores['f1_macro']:.4f}"
        )

        print(f"\n=== SMOTE pipeline — {name} (k_neighbors={k_smote}) ===")
        _, y_pred_sm, sm_scores = _fit_smote_model(
            name,
            factory,
            X_train,
            y_train_arr,
            X_test,
            y_test_arr,
            le,
            cv,
            tcfg,
            k_smote,
            nj,
        )
        smote_models[name] = sm_scores
        y_hat_report = y_pred_sm
        print(
            f"{name}: acc={sm_scores['accuracy']:.4f} "
            f"f1_macro={sm_scores['f1_macro']:.4f}"
        )

    if y_hat_report is None:
        raise RuntimeError("No SMOTE models were trained.")

    labels_idx = np.arange(len(le.classes_))
    report = classification_report(
        y_test_arr,
        y_hat_report,
        labels=labels_idx,
        target_names=list(le.classes_),
        output_dict=True,
        zero_division=0,
    )

    exp_meta_path = root / cfg["models"]["crop"]["experiment_metadata_path"]
    crop_meta = {
        "experiment": "merged_smote_class_weight",
        "training_date": date.today().isoformat(),
        "smote_k_neighbors": k_smote,
        "raw_merged_holdout": raw_models,
        "smote_balanced_holdout": smote_models,
        "classification_report": report,
        "classification_report_from_smote_model": model_order[-1],
    }
    with open(exp_meta_path, "w", encoding="utf-8") as fh:
        json.dump(crop_meta, fh, indent=2, default=str)

    chart_path = art_reports / "imbalance_experiment.png"
    _plot_imbalance_comparison(
        model_order,
        [raw_models[m]["accuracy"] for m in model_order],
        [smote_models[m]["accuracy"] for m in model_order],
        [raw_models[m]["f1_macro"] for m in model_order],
        [smote_models[m]["f1_macro"] for m in model_order],
        chart_path,
    )

    print("\nSaved:")
    print(f"  Experiment metadata: {exp_meta_path}")
    print(f"  Chart: {chart_path}")
    print("Run: python src/evaluation/generate_report_data.py")


if __name__ == "__main__":
    main()
