"""Unit tests for basic health checks."""

from servo.healthcheck import check_workspace
from saheeli.healthcheck import check_config

def test_servo_check_workspace(tmp_path):
    """check_workspace returns True when the path exists."""
    path = tmp_path / "workspace"
    path.mkdir()
    assert check_workspace(path)

def test_saheeli_check_config():
    """check_config returns True for a valid config file."""
    assert check_config()
