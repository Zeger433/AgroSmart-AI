"""Agronomic input validation shared by Flask and tests."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Tuple

# API field names expected in JSON payloads
REQUIRED_PREDICTION_FIELDS: List[str] = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall",
    "soil_type",
    "country",
    "pesticides",
]

_FIELD_LABELS: Dict[str, str] = {
    "N": "Nitrogen (N)",
    "P": "Phosphorus (P)",
    "K": "Potassium (K)",
    "ph": "pH",
    "temperature": "Temperature",
    "humidity": "Humidity",
    "rainfall": "Rainfall",
    "pesticides": "Pesticides",
}


def _parse_float(value: Any) -> float:
    if value is None or value == "":
        raise ValueError("missing numeric value")
    return float(value)


def validate_prediction_payload(
    data: Mapping[str, Any], ranges: Mapping[str, Tuple[float, float]]
) -> Dict[str, float]:
    """Validate prediction JSON body against agronomic ranges.

    Args:
        data: Parsed JSON dict from the client.
        ranges: Mapping field name -> (min, max) inclusive.

    Returns:
        Dict of parsed float values for all validated numeric fields.

    Raises:
        ValueError: With a human-readable message suitable for HTTP 400 responses.
    """
    for field in REQUIRED_PREDICTION_FIELDS:
        if field not in data or data[field] in (None, ""):
            raise ValueError(f"Missing required field: {field}")

    out: Dict[str, float] = {}
    for field, (lo, hi) in ranges.items():
        if field not in ("N", "P", "K", "ph", "temperature", "humidity", "rainfall", "pesticides"):
            continue
        try:
            val = _parse_float(data.get(field))
        except (TypeError, ValueError):
            raise ValueError(f"Invalid numeric value for field: {field}") from None
        if val < lo or val > hi:
            label = _FIELD_LABELS.get(field, field)
            raise ValueError(f"Invalid input: {label} must be between {lo} and {hi}.")
        out[field] = val
    return out
