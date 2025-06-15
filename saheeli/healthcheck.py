import sys
from pydantic import ValidationError
import yaml
from .config import load_config


def check_config() -> bool:
    """Return True if configuration loads successfully."""
    try:
        load_config()
        return True
    except (yaml.YAMLError, ValidationError, FileNotFoundError):
        return False


def main() -> int:
    """Health check entrypoint for the Saheeli container."""
    if check_config():
        print("OK")
        return 0
    print("Configuration error", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
