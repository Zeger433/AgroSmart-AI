"""Model artifact smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))


def _paths():
    root = _ROOT
    return (
        root / "artifacts" / "models" / "crop_model.pkl",
        root / "artifacts" / "models" / "yield_model.pkl",
    )


@pytest.mark.skipif(not _paths()[0].exists(), reason="crop model not trained yet")
def test_crop_model_loads() -> None:
    art = joblib.load(_paths()[0])
    assert "pipeline" in art
    assert "label_encoder" in art


@pytest.mark.skipif(not _paths()[1].exists(), reason="yield model not trained yet")
def test_yield_model_loads() -> None:
    pipe = joblib.load(_paths()[1])
    assert isinstance(pipe, Pipeline)


@pytest.mark.skipif(not _paths()[0].exists(), reason="crop model not trained yet")
def test_crop_prediction_shape() -> None:
    art = joblib.load(_paths()[0])
    pipe = art["pipeline"]
    le = art["label_encoder"]
    X = pd.DataFrame(
        [
            {
                "N": 50.0,
                "P": 50.0,
                "K": 50.0,
                "temperature": 25.0,
                "humidity": 60.0,
                "ph": 6.5,
                "rainfall": 100.0,
                "Soil_Type": "loam",
            }
        ]
    )
    pred = pipe.predict(X)
    assert pred.shape == (1,)


@pytest.mark.skipif(not _paths()[0].exists(), reason="crop model not trained yet")
def test_crop_prediction_valid_class() -> None:
    art = joblib.load(_paths()[0])
    pipe = art["pipeline"]
    le = art["label_encoder"]
    X = pd.DataFrame(
        [
            {
                "N": 50.0,
                "P": 50.0,
                "K": 50.0,
                "temperature": 25.0,
                "humidity": 60.0,
                "ph": 6.5,
                "rainfall": 100.0,
                "Soil_Type": "loam",
            }
        ]
    )
    idx = int(pipe.predict(X)[0])
    name = le.inverse_transform([idx])[0]
    assert name in set(le.classes_)


@pytest.mark.skipif(not _paths()[1].exists(), reason="yield model not trained yet")
def test_yield_prediction_positive() -> None:
    pipe = joblib.load(_paths()[1])
    X = pd.DataFrame(
        [
            {
                "Area": "India",
                "Item": "rice",
                "average_rain_fall_mm_per_year": 200.0,
                "pesticides_tonnes": 50000.0,
                "avg_temp": 25.0,
            }
        ]
    )
    y = pipe.predict(X)[0]
    assert float(y) > 0


@pytest.mark.skipif(not _paths()[0].exists(), reason="crop model not trained yet")
def test_rice_inputs_predict_rice() -> None:
    art = joblib.load(_paths()[0])
    pipe = art["pipeline"]
    le = art["label_encoder"]
    X = pd.DataFrame(
        [
            {
                "N": 90.0,
                "P": 42.0,
                "K": 43.0,
                "temperature": 20.9,
                "humidity": 82.0,
                "ph": 6.5,
                "rainfall": 202.9,
                "Soil_Type": "loam",
            }
        ]
    )
    idx = int(pipe.predict(X)[0])
    name = str(le.inverse_transform([idx])[0]).lower()
    assert name == "rice"
