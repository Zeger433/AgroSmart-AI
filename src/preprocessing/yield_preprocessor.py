"""Yield dataset loading and preprocessing."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


def build_yield_preprocessor() -> ColumnTransformer:
    """Preprocessor matching the deployed yield regression schema."""
    categorical_features = ["Area", "Item"]
    numerical_features = [
        "average_rain_fall_mm_per_year",
        "pesticides_tonnes",
        "avg_temp",
    ]
    return ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_features,
            ),
            ("num", "passthrough", numerical_features),
        ]
    )


def load_yield_dataframe(raw_dir: Path) -> Tuple[pd.DataFrame, pd.Series]:
    """Load ``yield_df.csv`` and return feature matrix ``X`` and target ``y``."""
    df = pd.read_csv(raw_dir / "yield_df.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    df = df.dropna()
    if df["average_rain_fall_mm_per_year"].dtype == object:
        df["average_rain_fall_mm_per_year"] = pd.to_numeric(
            df["average_rain_fall_mm_per_year"], errors="coerce"
        )
        df = df.dropna()
    df["Item"] = df["Item"].astype(str).str.lower().str.strip()
    X = df[
        [
            "Area",
            "Item",
            "average_rain_fall_mm_per_year",
            "pesticides_tonnes",
            "avg_temp",
        ]
    ]
    y = df["hg/ha_yield"]
    return X, y
