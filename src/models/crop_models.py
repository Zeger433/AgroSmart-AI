"""Classifier definitions for crop recommendation."""

from __future__ import annotations

from typing import Callable, Dict

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier


def crop_classifier_factories(
    *,
    class_weight_balanced: bool = False,
) -> Dict[str, Callable[[ColumnTransformer], Pipeline]]:
    """Return factory callables that build unfitted sklearn ``Pipeline`` objects.

    Args:
        class_weight_balanced: If True, set ``class_weight='balanced'`` on RF and
            SVC. ``GradientBoostingClassifier`` has no ``class_weight``; callers
            should use ``sample_weight`` from ``compute_sample_weight`` if needed.
            XGBoost and KNN are unchanged.

    Returns:
        Mapping from canonical model name to factory taking a preprocessor.
    """
    cw_rf = "balanced" if class_weight_balanced else None
    cw_svc = "balanced" if class_weight_balanced else None

    def rf(pre: ColumnTransformer) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", pre),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=100,
                        random_state=42,
                        n_jobs=-1,
                        class_weight=cw_rf,
                    ),
                ),
            ]
        )

    def xgb(pre: ColumnTransformer) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", pre),
                (
                    "classifier",
                    XGBClassifier(
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=6,
                        subsample=0.9,
                        colsample_bytree=0.9,
                        objective="multi:softprob",
                        eval_metric="mlogloss",
                        use_label_encoder=False,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        )

    def svm(pre: ColumnTransformer) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", pre),
                ("scaler", StandardScaler(with_mean=True)),
                (
                    "classifier",
                    SVC(
                        kernel="rbf",
                        C=1.0,
                        gamma="scale",
                        probability=True,
                        random_state=42,
                        class_weight=cw_svc,
                    ),
                ),
            ]
        )

    def knn(pre: ColumnTransformer) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", pre),
                ("scaler", StandardScaler(with_mean=True)),
                (
                    "classifier",
                    KNeighborsClassifier(
                        n_neighbors=7,
                        weights="distance",
                        metric="minkowski",
                        p=2,
                        n_jobs=-1,
                    ),
                ),
            ]
        )

    def gbc(pre: ColumnTransformer) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", pre),
                (
                    "classifier",
                    GradientBoostingClassifier(
                        random_state=42,
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=3,
                    ),
                ),
            ]
        )

    return {
        "RandomForest": rf,
        "XGBoost": xgb,
        "SVM": svm,
        "KNN": knn,
        "GradientBoosting": gbc,
    }
