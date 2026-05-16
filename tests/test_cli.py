import json
from pathlib import Path

from typer.testing import CliRunner

from jwt_cli_orchestrator.cli import app

runner = CliRunner()


def test_init_creates_config(tmp_path: Path):
    config_file = tmp_path / "myconfig.yaml"
    result = runner.invoke(app, ["init", str(config_file)])
    assert result.exit_code == 0
    assert config_file.exists()
    content = config_file.read_text()
    assert "services" in content


def test_auth_login_and_verify(tmp_path: Path, monkeypatch):
    # Login
    login_res = runner.invoke(app, ["auth", "login", "--user", "alice", "--role", "admin"])
    assert login_res.exit_code == 0
    token = login_res.stdout.splitlines()[-1]
    # Verify
    verify_res = runner.invoke(app, ["auth", "verify", "--token", token])
    assert verify_res.exit_code == 0
    payload = json.loads(verify_res.stdout.splitlines()[-1].replace("'", '"'))
    assert payload["sub"] == "alice"
    assert payload["role"] == "admin"
