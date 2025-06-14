from pathlib import Path
import json


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())
