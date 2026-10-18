"""Model loading and prediction orchestration for the Flask API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd
from loguru import logger

from sklearn.pipeline import Pipeline

from src.utils.paths import load_config


def _feature_matrix_at_classifier(pipe: Pipeline, X: pd.DataFrame) -> Any:
    """Apply every pipeline step before ``classifier`` (preprocessor, scaler, …).

    Args:
        pipe: Fitted sklearn ``Pipeline`` whose final classifier step is named
            ``classifier``.
        X: Raw feature frame matching the pipeline's first step.

    Returns:
        Array-like feature matrix accepted by ``classifier.predict_proba``.
    """
    Xt: Any = X
    for name, step in pipe.steps:
        if name == "classifier":
            break
        if hasattr(step, "transform"):
            Xt = step.transform(Xt)
    return Xt


def _crop_prediction_confidence(
    pipe: Pipeline,
    X: pd.DataFrame,
    le: Any,
) -> float:
    """Probability of the predicted class, aligned with ``LabelEncoder`` codes.

    ``predict_proba`` column ``j`` corresponds to ``clf.classes_[j]``, which must
    match the integer codes produced by the saved ``LabelEncoder`` (0 …
    ``len(le.classes_) - 1``). We pick the column whose class id equals the
    pipeline's integer prediction — not ``argmax(proba)`` alone when column
    order might differ from code order.

    Args:
        pipe: Fitted crop ``Pipeline`` with a ``classifier`` step.
        X: Single-row (or batch) feature frame.
        le: The ``LabelEncoder`` saved with the artifact (same fit as training).

    Returns:
        Confidence in ``[0, 1]`` for the predicted class.
    """
    clf = pipe.named_steps["classifier"]
    Xt = _feature_matrix_at_classifier(pipe, X)
    proba_row = np.asarray(clf.predict_proba(Xt)[0], dtype=float).ravel()
    clf_classes = np.asarray(clf.classes_)

    pred = int(np.asarray(pipe.predict(X), dtype=int).ravel()[0])

    # sklearn: proba[i] is P(y == clf.classes_[i] | X)
    match = np.nonzero(clf_classes.astype(int) == pred)[0]
    if match.size > 0:
        j = int(match[0])
        conf = float(proba_row[j])
    else:
        logger.warning(
            "Predicted code {} not found in clf.classes_ {}; using max proba",
            pred,
            clf_classes,
        )
        conf = float(np.max(proba_row))

    # Optional sanity: expected n_classes matches saved encoder
    n_le = len(le.classes_)
    if proba_row.shape[0] != n_le:
        logger.debug(
            "proba length {} vs LabelEncoder n_classes {}; clf.classes_={}",
            proba_row.shape[0],
            n_le,
            clf_classes,
        )

    return float(min(max(conf, 0.0), 1.0))


def _crop_prediction_confidence_fallback(pipe: Any, X: pd.DataFrame, _le: Any) -> float:
    """Same alignment logic when only the outer pipeline exposes ``predict_proba``."""
    if not hasattr(pipe, "predict_proba") or not hasattr(pipe, "classes_"):
        return 0.0
    proba_row = np.asarray(pipe.predict_proba(X)[0], dtype=float).ravel()
    clf_classes = np.asarray(pipe.classes_)
    pred = int(np.asarray(pipe.predict(X), dtype=int).ravel()[0])
    match = np.nonzero(clf_classes.astype(int) == pred)[0]
    if match.size > 0:
        return float(min(max(float(proba_row[int(match[0])]), 0.0), 1.0))
    return float(min(max(float(np.max(proba_row)), 0.0), 1.0))


class ModelPredictor:
    """Loads trained crop and yield models and runs end-to-end inference."""

    def __init__(self, config: Dict[str, Any], root: Path) -> None:
        """Attach configuration and resolve absolute artifact paths.

        Args:
            config: Parsed ``config/config.yaml`` dictionary.
            root: Project root directory.
        """
        self._cfg = config
        self._root = root
        self._crop_artifact: Optional[Dict[str, Any]] = None
        self._crop_meta: Optional[Dict[str, Any]] = None
        self._yield_model: Optional[Any] = None
        self._yield_meta: Optional[Dict[str, Any]] = None
        self._load_models()

    @classmethod
    def from_default_config(cls) -> "ModelPredictor":
        """Construct predictor using the default YAML configuration."""
        cfg = load_config()
        root = Path(__file__).resolve().parents[1]
        return cls(cfg, root)

    def _load_models(self) -> None:
        """Load serialized estimators and metadata from disk."""
        self._crop_meta = None
        self._yield_meta = None
        crop_path = self._root / self._cfg["models"]["crop"]["artifact_path"]
        crop_meta_path = self._root / self._cfg["models"]["crop"]["metadata_path"]
        yield_path = self._root / self._cfg["models"]["yield"]["artifact_path"]
        meta_path = self._root / self._cfg["models"]["yield"]["metadata_path"]
        try:
            if crop_path.exists():
                self._crop_artifact = joblib.load(crop_path)
                logger.info("Loaded crop model from {}", crop_path)
            else:
                logger.warning("Crop model missing at {}", crop_path)
            if crop_meta_path.exists():
                with open(crop_meta_path, "r", encoding="utf-8") as fh:
                    self._crop_meta = json.load(fh)
            if yield_path.exists():
                self._yield_model = joblib.load(yield_path)
                logger.info("Loaded yield model from {}", yield_path)
            else:
                logger.warning("Yield model missing at {}", yield_path)
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as fh:
                    self._yield_meta = json.load(fh)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed loading models: {}", exc)

    def reload(self) -> None:
        """Reload artifacts from disk (useful in tests)."""
        self._load_models()

    def predict(
        self,
        *,
        N: float,
        P: float,
        K: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float,
        soil_type: str,
        country: str,
        pesticides: float,
        land_area: float = 0.0,
    ) -> Dict[str, Any]:
        """Run crop classification followed by yield regression.

        Args:
            N, P, K: Soil macronutrients.
            temperature: Celsius.
            humidity: Relative humidity percent.
            ph: Soil pH.
            rainfall: Millimetres per year.
            soil_type: Soil class label.
            country: Country / area label for yield model.
            pesticides: National / regional pesticide usage (tonnes).
            land_area: Optional hectares for total production estimate.

        Returns:
            Dictionary suitable for JSON serialization to the web client.

        Raises:
            RuntimeError: If models are not available on disk.
        """
        if not self._crop_artifact or not self._yield_model:
            raise RuntimeError("Models are not loaded")

        soil = (soil_type or "loam").lower().strip()
        crop_df = pd.DataFrame(
            [
                {
                    "N": N,
                    "P": P,
                    "K": K,
                    "temperature": temperature,
                    "humidity": humidity,
                    "ph": ph,
                    "rainfall": rainfall,
                    "Soil_Type": soil,
                }
            ]
        )
        pipe = self._crop_artifact["pipeline"]
        le = self._crop_artifact["label_encoder"]
        idx = int(pipe.predict(crop_df)[0])
        if hasattr(le, "inverse_transform"):
            crop_name = str(le.inverse_transform([idx])[0])
        else:
            crop_name = str(idx)
        crop_lower = crop_name.lower().strip()

        confidence_pct: Optional[float] = None
        try:
            if isinstance(pipe, Pipeline) and "classifier" in pipe.named_steps:
                clf_step = pipe.named_steps["classifier"]
                if hasattr(clf_step, "predict_proba"):
                    conf_frac = _crop_prediction_confidence(pipe, crop_df, le)
                    confidence_pct = round(conf_frac * 100.0, 1)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Classifier-step confidence failed ({}); falling back.", exc)
        if confidence_pct is None and hasattr(pipe, "predict_proba"):
            conf_frac = _crop_prediction_confidence_fallback(pipe, crop_df, le)
            confidence_pct = round(conf_frac * 100.0, 1)

        yield_df = pd.DataFrame(
            [
                {
                    "Area": country,
                    "Item": crop_lower,
                    "average_rain_fall_mm_per_year": rainfall,
                    "pesticides_tonnes": pesticides,
                    "avg_temp": temperature,
                }
            ]
        )
        y_hg_ha = float(self._yield_model.predict(yield_df)[0])
        y_hg_ha = max(y_hg_ha, 0.0)
        y_tons = y_hg_ha / 10_000.0

        mae = 0.0
        if self._yield_meta:
            if "models" in self._yield_meta and self._yield_meta.get("best_model"):
                bm = str(self._yield_meta["best_model"])
                mdl = (self._yield_meta.get("models") or {}).get(bm, {})
                mae = float(mdl.get("mae", 0.0))
            else:
                mae = float(self._yield_meta.get("metrics", {}).get("mae", 0.0))
        mae_tons = mae / 10_000.0
        if self._yield_meta:
            r2 = float(
                self._yield_meta.get("best_r2")
                or self._yield_meta.get("metrics", {}).get("r2", 0.0)
            )
        else:
            r2 = 0.0
        feat = {}
        if self._yield_meta:
            feat = self._yield_meta.get("feature_importance", {}) or {}

        explanation = self._build_explanation(country, feat)

        total_production = None
        if land_area and land_area > 0:
            total_production = round(y_tons * land_area, 2)

        return {
            "success": True,
            "crop": crop_name.title(),
            "crop_key": crop_lower,
            "yield": round(y_tons, 2),
            "currency": "tons/ha",
            "confidence": {
                "min": round(max(0.0, y_tons - mae_tons), 2),
                "max": round(y_tons + mae_tons, 2),
                "r2_score": r2,
            },
            "confidence_pct": confidence_pct,
            "explanation": explanation,
            "feature_importance": feat,
            "total_production": total_production,
            "crop_model": (self._crop_meta or {}).get("best_model")
            or (self._crop_meta or {}).get("model_used"),
            "yield_model": (self._yield_meta or {}).get("best_model")
            if self._yield_meta and "best_model" in self._yield_meta
            else "RandomForest",
        }

    def _build_explanation(self, country: str, feat: Dict[str, Any]) -> str:
        """Create a short natural-language explanation."""
        if not feat:
            return f"Yield estimate uses historical patterns for {country}."
        top = sorted(feat.items(), key=lambda kv: kv[1], reverse=True)[:2]
        parts = [f"{k} ({v}%)" for k, v in top]
        return (
            f"Yield is mainly influenced by {', '.join(parts)}. "
            f"Predictions are informed by data for {country}."
        )

    def model_info(self) -> Dict[str, Any]:
        """Return metadata for the `/model-info` endpoint."""
        return {
            "crop": self._crop_meta or {},
            "yield": self._yield_meta or {},
        }
