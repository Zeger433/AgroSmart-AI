"""Validator unit tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from src.utils.validators import validate_prediction_payload  # noqa: E402

_RANGES = {
    "N": (0, 140),
    "P": (5, 145),
    "K": (5, 205),
    "ph": (3.5, 9.0),
    "temperature": (8, 43),
    "humidity": (14, 100),
    "rainfall": (20, 300),
    "pesticides": (0, 1_000_000),
}


def test_valid_inputs_pass() -> None:
    data = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 25,
        "humidity": 70,
        "ph": 6.5,
        "rainfall": 120,
        "soil_type": "loam",
        "country": "India",
        "pesticides": 1000,
    }
    out = validate_prediction_payload(data, _RANGES)
    assert out["N"] == 90.0


def test_ph_out_of_range_fails() -> None:
    data = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 25,
        "humidity": 70,
        "ph": 15,
        "rainfall": 120,
        "soil_type": "loam",
        "country": "India",
        "pesticides": 1000,
    }
    with pytest.raises(ValueError):
        validate_prediction_payload(data, _RANGES)


def test_nitrogen_out_of_range_fails() -> None:
    data = {
        "N": 200,
        "P": 42,
        "K": 43,
        "temperature": 25,
        "humidity": 70,
        "ph": 6.5,
        "rainfall": 120,
        "soil_type": "loam",
        "country": "India",
        "pesticides": 1000,
    }
    with pytest.raises(ValueError):
        validate_prediction_payload(data, _RANGES)


def test_temperature_below_minimum_fails() -> None:
    data = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 5,
        "humidity": 70,
        "ph": 6.5,
        "rainfall": 120,
        "soil_type": "loam",
        "country": "India",
        "pesticides": 1000,
    }
    with pytest.raises(ValueError):
        validate_prediction_payload(data, _RANGES)
