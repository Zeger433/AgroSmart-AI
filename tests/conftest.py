"""Pytest fixtures for the Flask application."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


@pytest.fixture()
def client():
    """Flask test client with fresh app factory."""
    from app.main import create_app

    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
