"""Flask application factory and HTTP routes for AgroSmart AI."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Tuple

from dotenv import load_dotenv
import os

from flask import Flask, jsonify, request, send_from_directory
from loguru import logger

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

load_dotenv(_ROOT / ".env", override=False)

from app.predictor import ModelPredictor  # noqa: E402
from src.utils.logger import configure_logging  # noqa: E402
from src.utils.paths import load_config  # noqa: E402
from src.utils.validators import validate_prediction_payload  # noqa: E402

FEATURE_LABELS: Dict[str, str] = {
    "Item_crop": "Crop Type",
    "Area_country": "Region / Country",
    "pesticides_tonnes": "Pesticide Usage",
    "avg_temp": "Average Temperature",
    "avg_rain": "Average Rainfall",
    "average_rain_fall_mm_per_year": "Average Rainfall",
    "Item": "Crop Type",
    "Area": "Region / Country",
}


def _humanize_prediction_response(out: Dict[str, Any]) -> Dict[str, Any]:
    """Map internal yield-feature keys to human-readable labels for the UI."""
    text = str(out.get("explanation", ""))
    for raw in sorted(FEATURE_LABELS.keys(), key=len, reverse=True):
        text = text.replace(raw, FEATURE_LABELS[raw])
    out["explanation"] = text
    fi = out.get("feature_importance") or {}
    if isinstance(fi, dict):
        out["feature_importance"] = {
            FEATURE_LABELS.get(k, k): (float(v) if isinstance(v, (int, float)) else v)
            for k, v in fi.items()
        }
    return out


def _ranges_from_cfg(cfg: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
    out_ranges: Dict[str, Tuple[float, float]] = {}
    for k, pair in cfg.get("validation", {}).items():
        out_ranges[k] = (float(pair[0]), float(pair[1]))
    return out_ranges


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Configured ``Flask`` instance with routes registered.
    """
    configure_logging(level="INFO", log_file="artifacts/logs/app.log")
    cfg = load_config()
    base = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        template_folder=str(base / "templates"),
        static_folder=str(base / "static"),
        static_url_path="/static",
    )
    app.config["AGRO_CONFIG"] = cfg
    app.config["VALIDATION_RANGES"] = _ranges_from_cfg(cfg)
    app.config["COUNTRY_DEFAULTS"] = cfg.get("country_defaults", {})
    try:
        app.config["PREDICTOR"] = ModelPredictor(cfg, _ROOT)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Predictor init failed: {}", exc)
        app.config["PREDICTOR"] = None

    @app.before_request
    def _log_request() -> None:
        logger.info("{} {}", request.method, request.path)

    @app.get("/health")
    def health() -> Any:
        """Liveness probe for orchestrators."""
        return jsonify({"status": "ok"})

    @app.get("/model-info")
    def model_info() -> Any:
        """Expose persisted training metadata."""
        pred = app.config.get("PREDICTOR")
        if pred is None:
            return jsonify({"error": "Models not loaded"}), 500
        return jsonify(pred.model_info())

    @app.post("/get_defaults")
    def get_defaults() -> Any:
        """Return configured climate defaults for a country."""
        body = request.get_json(silent=True) or {}
        country = (body.get("country") or "").strip()
        defaults_map: Dict[str, Any] = app.config.get("COUNTRY_DEFAULTS", {})
        if not country:
            return jsonify({"error": "Missing country"}), 400
        if country not in defaults_map:
            return jsonify({"error": "Country not found"}), 404
        d = defaults_map[country]
        return jsonify(
            {
                "success": True,
                "rainfall": float(d["rainfall"]),
                "temperature": float(d["temperature"]),
                "pesticides": float(d["pesticides"]),
            }
        )

    @app.post("/predict")
    def predict() -> Any:
        """Validate input and return crop + yield JSON."""
        pred: ModelPredictor | None = app.config.get("PREDICTOR")
        if pred is None:
            return jsonify({"error": "Models not loaded"}), 500
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Expected JSON body"}), 400
        ranges = app.config["VALIDATION_RANGES"]
        try:
            nums = validate_prediction_payload(data, ranges)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        try:
            land_area = float(data.get("land_area") or 0)
        except (TypeError, ValueError):
            land_area = 0.0
        try:
            out = pred.predict(
                N=nums["N"],
                P=nums["P"],
                K=nums["K"],
                temperature=nums["temperature"],
                humidity=nums["humidity"],
                ph=nums["ph"],
                rainfall=nums["rainfall"],
                soil_type=str(data.get("soil_type", "loam")),
                country=str(data.get("country", "India")),
                pesticides=nums["pesticides"],
                land_area=land_area,
            )
            _humanize_prediction_response(out)
            return jsonify(out)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Prediction failed: {}", exc)
            return jsonify({"error": "Prediction failed"}), 500

    react_dir = os.path.join(app.static_folder, "react")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_react(path: str) -> Any:
        """Serve the React SPA; API routes registered above take precedence."""
        if path and os.path.exists(os.path.join(react_dir, path)):
            return send_from_directory(react_dir, path)
        index_path = os.path.join(react_dir, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(react_dir, "index.html")
        return jsonify({"error": "Frontend not built. Run: cd frontend && npm run build"}), 503

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
