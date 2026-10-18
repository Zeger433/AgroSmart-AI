"""Project root and configuration loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


def project_root() -> Path:
    """Return absolute path to the agrosmart-ai project root."""
    return Path(__file__).resolve().parents[2]


def load_config(config_path: Path | None = None) -> Dict[str, Any]:
    """Load ``config/config.yaml`` from the project root.

    Args:
        config_path: Optional explicit path to YAML file.

    Returns:
        Parsed configuration dictionary.
    """
    root = project_root()
    path = config_path or (root / "config" / "config.yaml")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
