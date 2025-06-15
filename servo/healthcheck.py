"""Health check utilities for Servo containers."""

from pathlib import Path
import sys


def check_workspace(path: Path = Path("/workspace")) -> bool:
    """Return True if the workspace directory exists."""
    return path.exists()


def main() -> int:
    """Simple health check entrypoint."""
    if check_workspace():
        print("OK")
        return 0
    print("Workspace missing", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
