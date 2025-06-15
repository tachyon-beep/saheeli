from servo.healthcheck import check_workspace
from saheeli.healthcheck import check_config

def test_servo_check_workspace(tmp_path):
    path = tmp_path / "workspace"
    path.mkdir()
    assert check_workspace(path)

def test_saheeli_check_config():
    assert check_config()
