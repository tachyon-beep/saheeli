"""Utility helpers for file IO within the Servo container."""

from pathlib import Path
import json


def write_json(path: Path, data: dict) -> None:
    """Write a JSON document to ``path``."""
    path.write_text(json.dumps(data, indent=2))


def read_json(path: Path) -> dict:
    """Read and return JSON content from ``path``."""
    return json.loads(path.read_text())
