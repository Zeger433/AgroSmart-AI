"""Crop dataset loading and preprocessing helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


def build_crop_preprocessor() -> ColumnTransformer:
    """Build sklearn ``ColumnTransformer`` for crop features."""
    categorical_features = ["Soil_Type"]
    numerical_features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    return ColumnTransformer(
        transformers=[
            ("num", "passthrough", numerical_features),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_features,
            ),
        ]
    )


def load_balanced_baseline_crop_dataframe(raw_dir: Path) -> Tuple[pd.DataFrame, pd.Series]:
    """Load only ``Crop_recommendation.csv`` (balanced ~100 rows × 22 classes).

    Adds ``Soil_Type`` = ``loam`` so the schema matches merged / API pipelines.

    Args:
        raw_dir: Directory containing ``Crop_recommendation.csv``.

    Returns:
        ``(X, y)`` with ``y`` as lowercase string crop labels.
    """
    df = pd.read_csv(raw_dir / "Crop_recommendation.csv")
    df = df.dropna()
    df["Soil_Type"] = "loam"
    df["label"] = df["label"].astype(str).str.lower().str.strip()
    df["Soil_Type"] = df["Soil_Type"].astype(str).str.lower().str.strip()
    X = df.drop(columns=["label"])
    y = df["label"]
    return X, y


def load_combined_crop_dataframe(raw_dir: Path) -> Tuple[pd.DataFrame, pd.Series]:
    """Load and merge baseline + sensor crop datasets.

    Args:
        raw_dir: Directory containing ``Crop_recommendation.csv`` and
            ``sensor_Crop_Dataset.csv``.

    Returns:
        Tuple ``(X, y)`` where ``y`` is **raw string** crop labels (lowercase).
        The training script must fit exactly one ``LabelEncoder`` on ``y`` and
        use the resulting integer targets for all fitting, CV, and scoring.
    """
    df_basic = pd.read_csv(raw_dir / "Crop_recommendation.csv")
    df_sensor = pd.read_csv(raw_dir / "sensor_Crop_Dataset.csv")

    df_sensor = df_sensor.rename(
        columns={
            "Nitrogen": "N",
            "Phosphorus": "P",
            "Potassium": "K",
            "Temperature": "temperature",
            "Humidity": "humidity",
            "pH_Value": "ph",
            "Rainfall": "rainfall",
            "Crop": "label",
        }
    )
    if "Variety" in df_sensor.columns:
        df_sensor = df_sensor.drop(columns=["Variety"])

    df_basic["Soil_Type"] = "loam"
    common_cols = [
        "N",
        "P",
        "K",
        "temperature",
        "humidity",
        "ph",
        "rainfall",
        "Soil_Type",
        "label",
    ]
    df_basic = df_basic[common_cols]
    df_sensor = df_sensor[common_cols]

    df_final = pd.concat([df_basic, df_sensor], axis=0, ignore_index=True)
    df_final = df_final.dropna()
    df_final["label"] = df_final["label"].astype(str).str.lower().str.strip()
    df_final["Soil_Type"] = df_final["Soil_Type"].astype(str).str.lower().str.strip()

    X = df_final.drop(columns=["label"])
    y = df_final["label"]
    return X, y


def validation_ranges_from_config(cfg: Dict[str, Any]) -> Dict[str, tuple]:
    """Convert YAML validation lists to float tuples."""
    out: Dict[str, tuple] = {}
    for key, pair in cfg.get("validation", {}).items():
        lo, hi = float(pair[0]), float(pair[1])
        out[key] = (lo, hi)
    return out
