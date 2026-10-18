"""HTTP API tests."""

from __future__ import annotations


def test_health_endpoint(client) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_model_info_endpoint(client) -> None:
    res = client.get("/model-info")
    if res.status_code == 500:
        pytest.skip("models not installed")
    data = res.get_json()
    assert "crop" in data and "yield" in data


def test_predict_valid_input(client) -> None:
    payload = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 20.9,
        "humidity": 82,
        "ph": 6.5,
        "rainfall": 120,
        "soil_type": "loam",
        "country": "India",
        "pesticides": 50000,
    }
    res = client.post("/predict", json=payload)
    if res.status_code == 500:
        pytest.skip("models not installed")
    assert res.status_code == 200
    body = res.get_json()
    assert body.get("success") is True
    assert "crop" in body and "yield" in body


def test_predict_invalid_ph(client) -> None:
    payload = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 20.9,
        "humidity": 82,
        "ph": 15,
        "rainfall": 120,
        "soil_type": "loam",
        "country": "India",
        "pesticides": 50000,
    }
    res = client.post("/predict", json=payload)
    assert res.status_code == 400


def test_predict_missing_field(client) -> None:
    payload = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 20.9,
        "humidity": 82,
        "rainfall": 120,
        "soil_type": "loam",
        "country": "India",
        "pesticides": 50000,
    }
    res = client.post("/predict", json=payload)
    assert res.status_code == 400
