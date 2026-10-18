"""Regressor definitions for yield prediction."""

from __future__ import annotations

from typing import Callable, Dict

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from xgboost import XGBRegressor


def yield_regressor_factories() -> Dict[str, Callable[[ColumnTransformer], Pipeline]]:
    """Return factory callables for unfitted yield regression pipelines."""

    def rf(pre: ColumnTransformer) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", pre),
                (
                    "regressor",
                    RandomForestRegressor(
                        n_estimators=100,
                        max_depth=None,
                        min_samples_leaf=1,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        )

    def xgb(pre: ColumnTransformer) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", pre),
                (
                    "regressor",
                    XGBRegressor(
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=6,
                        subsample=0.9,
                        colsample_bytree=0.9,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        )

    def gbr(pre: ColumnTransformer) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", pre),
                (
                    "regressor",
                    GradientBoostingRegressor(
                        n_estimators=100,
                        learning_rate=0.1,
                        subsample=0.9,
                        max_depth=3,
                        random_state=42,
                    ),
                ),
            ]
        )

    def ridge(pre: ColumnTransformer) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", pre),
                ("scaler", StandardScaler(with_mean=True)),
                ("regressor", Ridge(alpha=1.0)),
            ]
        )

    def svr(pre: ColumnTransformer) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", pre),
                ("scaler", StandardScaler(with_mean=True)),
                (
                    "regressor",
                    SVR(kernel="rbf", C=1.0, epsilon=0.1, gamma="scale"),
                ),
            ]
        )

    return {
        "RandomForest": rf,
        "XGBoost": xgb,
        "GradientBoosting": gbr,
        "Ridge": ridge,
        "SVR": svr,
    }
