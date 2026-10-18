"""Tests for preprocessing helpers."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from src.preprocessing.crop_preprocessor import (  # noqa: E402
    load_balanced_baseline_crop_dataframe,
    load_combined_crop_dataframe,
)
from src.preprocessing.yield_preprocessor import load_yield_dataframe  # noqa: E402
from src.utils.paths import project_root  # noqa: E402


def test_balanced_baseline_crop_loads() -> None:
    raw = project_root() / "data" / "raw"
    X, y = load_balanced_baseline_crop_dataframe(raw)
    assert len(X) == 2200
    assert y.nunique() == 22


def test_crop_dataframe_loads() -> None:
    raw = project_root() / "data" / "raw"
    X, y = load_combined_crop_dataframe(raw)
    assert len(X) > 1000
    assert y.dtype == object or str(y.dtype) == "string"
    assert y.nunique() >= 22


def test_yield_dataframe_loads() -> None:
    raw = project_root() / "data" / "raw"
    X, y = load_yield_dataframe(raw)
    assert len(X) > 1000
    assert y.min() > 0
