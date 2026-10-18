"""Canonical yield regressor training with multi-model benchmarking."""

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
from sklearn.inspection import permutation_importance
from sklearn.model_selection import KFold, RandomizedSearchCV, cross_val_score, train_test_split

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.evaluation.compare_models import plot_horizontal_bar  # noqa: E402
from src.evaluation.metrics import model_comparison_bar, regression_scores  # noqa: E402
from src.models.yield_models import yield_regressor_factories  # noqa: E402
from src.preprocessing.yield_preprocessor import (  # noqa: E402
    build_yield_preprocessor,
    load_yield_dataframe,
)
from src.utils.paths import load_config, project_root  # noqa: E402


def _tune_rf_reg(pipe, X, y, cv, n_iter: int, random_state: int) -> Tuple[Any, Dict[str, Any]]:
    param_dist = {
        "regressor__n_estimators": randint(80, 150),
        "regressor__max_depth": [None, 8, 16, 24],
        "regressor__min_samples_leaf": randint(1, 5),
    }
    search = RandomizedSearchCV(
        estimator=pipe,
        param_distributions=param_dist,
        n_iter=n_iter,
        scoring="r2",
        cv=cv,
        n_jobs=-1,
        random_state=random_state,
        refit=True,
        verbose=1,
    )
    search.fit(X, y)
    best_params = {k.replace("regressor__", ""): v for k, v in search.best_params_.items()}
    return search.best_estimator_, {"best_params": best_params}


def _tune_xgb_reg(pipe, X, y, cv, n_iter: int, random_state: int) -> Tuple[Any, Dict[str, Any]]:
    param_dist = {
        "regressor__n_estimators": randint(80, 150),
        "regressor__learning_rate": uniform(0.03, 0.17),
        "regressor__max_depth": randint(3, 10),
        "regressor__subsample": uniform(0.7, 0.29),
    }
    search = RandomizedSearchCV(
        estimator=pipe,
        param_distributions=param_dist,
        n_iter=n_iter,
        scoring="r2",
        cv=cv,
        n_jobs=-1,
        random_state=random_state,
        refit=True,
        verbose=1,
    )
    search.fit(X, y)
    best_params = {k.replace("regressor__", ""): v for k, v in search.best_params_.items()}
    return search.best_estimator_, {"best_params": best_params}


def _permutation_feature_importance(
    model, X: pd.DataFrame, y: pd.Series, max_samples: int = 2500
) -> Dict[str, float]:
    """Compute permutation importance per original input column (percent)."""
    if len(X) > max_samples:
        Xs, _, ys, _ = train_test_split(X, y, train_size=max_samples, random_state=42)
    else:
        Xs, ys = X, y
    result = permutation_importance(
        model,
        Xs,
        ys,
        n_repeats=5,
        random_state=42,
        n_jobs=-1,
        scoring="r2",
    )
    names = list(X.columns)
    raw = result.importances_mean
    raw = np.maximum(raw, 0)
    total = float(np.sum(raw)) or 1.0
    return {names[i]: round(100.0 * float(raw[i]) / total, 2) for i in range(len(names))}


def main() -> None:
    """Train, compare, persist yield regressors."""
    cfg = load_config()
    root = project_root()
    raw_dir = root / cfg["paths"]["data_raw"]
    art_models = root / cfg["paths"]["artifacts_models"]
    art_reports = root / cfg["paths"]["artifacts_reports"]
    art_models.mkdir(parents=True, exist_ok=True)
    art_reports.mkdir(parents=True, exist_ok=True)

    tcfg = cfg["training"]
    cv = KFold(n_splits=int(tcfg["cv_folds"]), shuffle=True, random_state=int(tcfg["random_state"]))

    X, y = load_yield_dataframe(raw_dir)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=float(tcfg["test_size"]),
        random_state=int(tcfg["random_state"]),
    )

    factories = yield_regressor_factories()
    results_meta: Dict[str, Any] = {}
    r2_chart: Dict[str, float] = {}

    for name, factory in factories.items():
        print(f"\n=== Training {name} ===")
        pre = build_yield_preprocessor()
        pipe = factory(pre)

        X_tr, y_tr = X_train, y_train
        if name == "SVR" and len(X_tr) > 8000:
            X_tr, _, y_tr, _ = train_test_split(
                X_tr, y_tr, train_size=8000, random_state=int(tcfg["random_state"])
            )

        if name in ("RandomForest", "XGBoost"):
            n_iter = int(tcfg["search_n_iter_rf"] if name == "RandomForest" else tcfg["search_n_iter_xgb"])
            tuned, extra = (
                _tune_rf_reg(pipe, X_tr, y_tr, cv, n_iter, int(tcfg["random_state"]))
                if name == "RandomForest"
                else _tune_xgb_reg(pipe, X_tr, y_tr, cv, n_iter, int(tcfg["random_state"]))
            )
            cv_r2 = cross_val_score(
                clone(tuned), X_train, y_train, cv=cv, scoring="r2", n_jobs=-1
            )
            fitted = tuned
            meta_extra = extra
        else:
            fitted = clone(pipe)
            fitted.fit(X_tr, y_tr)
            cv_r2 = cross_val_score(
                clone(pipe), X_train, y_train, cv=cv, scoring="r2", n_jobs=-1
            )
            meta_extra = {"best_params": {}}

        y_pred = fitted.predict(X_test)
        scores = regression_scores(np.asarray(y_test), y_pred)
        results_meta[name] = {
            **scores,
            "cv_r2_mean": float(np.mean(cv_r2)),
            "cv_r2_std": float(np.std(cv_r2)),
            **meta_extra,
        }
        r2_chart[name] = scores["r2"]
        print(
            f"{name}: R2={scores['r2']:.4f} MAE={scores['mae']:.1f} "
            f"cv_R2={np.mean(cv_r2):.4f}+/-{np.std(cv_r2):.4f}"
        )

    best_name = max(r2_chart, key=r2_chart.get)
    print(f"\nBest model by R2 on hold-out: {best_name}")

    pre_best = build_yield_preprocessor()
    best_template = factories[best_name](pre_best)
    if best_name in ("RandomForest", "XGBoost"):
        final_estimator, _ = (
            _tune_rf_reg(
                best_template,
                X,
                y,
                cv,
                int(tcfg["search_n_iter_rf"]),
                int(tcfg["random_state"]),
            )
            if best_name == "RandomForest"
            else _tune_xgb_reg(
                best_template,
                X,
                y,
                cv,
                int(tcfg["search_n_iter_xgb"]),
                int(tcfg["random_state"]),
            )
        )
    else:
        final_estimator = clone(best_template)
        X_fit, y_fit = X, y
        if best_name == "SVR" and len(X) > 8000:
            X_fit, _, y_fit, _ = train_test_split(
                X, y, train_size=8000, random_state=int(tcfg["random_state"])
            )
        final_estimator.fit(X_fit, y_fit)

    feat_imp = _permutation_feature_importance(final_estimator, X_test, y_test)
    # Friendly keys for metadata (match spec example)
    feat_imp_out = {
        "Item_crop": feat_imp.get("Item", 0.0),
        "Area_country": feat_imp.get("Area", 0.0),
        "pesticides_tonnes": feat_imp.get("pesticides_tonnes", 0.0),
        "avg_temp": feat_imp.get("avg_temp", 0.0),
        "avg_rain": feat_imp.get("average_rain_fall_mm_per_year", 0.0),
    }

    yield_meta: Dict[str, Any] = {
        "best_model": best_name,
        "best_r2": float(r2_chart[best_name]),
        "training_date": date.today().isoformat(),
        "models": results_meta,
        "feature_importance": feat_imp_out,
    }

    meta_path = root / cfg["models"]["yield"]["metadata_path"]
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(yield_meta, fh, indent=2, default=str)

    model_path = root / cfg["models"]["yield"]["artifact_path"]
    joblib.dump(final_estimator, model_path)

    model_comparison_bar(
        list(r2_chart.keys()),
        list(r2_chart.values()),
        "R2 (hold-out test)",
        "Yield regressor comparison",
        str(art_reports / "yield_model_comparison.png"),
    )
    plot_horizontal_bar(
        list(feat_imp_out.keys()),
        list(feat_imp_out.values()),
        "Permutation importance (% of total)",
        "Feature importance (best yield model)",
        str(art_reports / "feature_importance.png"),
    )

    print("\nSaved:")
    print(f"  Model: {model_path}")
    print(f"  Metadata: {meta_path}")
    print(f"  Reports: {art_reports}")


if __name__ == "__main__":
    main()
