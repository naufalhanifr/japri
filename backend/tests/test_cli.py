import io

import pytest

from app import cli
from app.db import connect
from conftest import EMAIL, PASSWORD, login


@pytest.fixture
def env(settings):
    return {"JAPRI_DB_PATH": settings.db_path}


def run(monkeypatch, env, argv, password=None):
    if password is not None:
        monkeypatch.setattr("sys.stdin", io.StringIO(password + "\n"))
    return cli.main(argv, env)


def test_migrate_create_admin_and_login(monkeypatch, env, settings, capsys):
    from fastapi.testclient import TestClient

    from app.main import create_app

    assert run(monkeypatch, env, ["migrate"]) == 0
    argv = ["create-admin", "--email", EMAIL, "--display-name", "Admin", "--password-stdin"]
    assert run(monkeypatch, env, argv, PASSWORD) == 0
    out = capsys.readouterr()
    assert PASSWORD not in out.out + out.err
    client = TestClient(create_app(settings), base_url="https://testserver")
    assert login(client).status_code == 200


def test_short_password_rejected(monkeypatch, env, capsys):
    run(monkeypatch, env, ["migrate"])
    argv = ["create-admin", "--email", EMAIL, "--display-name", "Admin", "--password-stdin"]
    assert run(monkeypatch, env, argv, "pendek") == 1
    assert "minimal 12" in capsys.readouterr().err
    assert connect(env["JAPRI_DB_PATH"]).execute("SELECT COUNT(*) FROM admin").fetchone()[0] == 0


def test_second_admin_rejected(monkeypatch, env, capsys):
    run(monkeypatch, env, ["migrate"])
    run(monkeypatch, env, ["create-admin", "--email", EMAIL, "--display-name", "A", "--password-stdin"], PASSWORD)
    argv = ["create-admin", "--email", "b@example.test", "--display-name", "B", "--password-stdin"]
    assert run(monkeypatch, env, argv, PASSWORD) == 1
    assert "sudah ada" in capsys.readouterr().err


def test_create_admin_needs_migrated_schema(monkeypatch, env, capsys):
    argv = ["create-admin", "--email", EMAIL, "--display-name", "A", "--password-stdin"]
    assert run(monkeypatch, env, argv, PASSWORD) == 1
    assert "migrate" in capsys.readouterr().err


def test_reset_password_revokes_sessions(monkeypatch, env, session, settings):
    client, _ = session
    new = "kata-sandi-baru-5678"
    assert run(monkeypatch, env, ["reset-password", "--email", EMAIL, "--password-stdin"], new) == 0
    assert client.get("/api/admin/me").status_code == 401
    assert login(client, password=PASSWORD).status_code == 401
    assert login(client, password=new).status_code == 200


def test_reset_unknown_email_fails(monkeypatch, env, admin_id, capsys):
    assert run(monkeypatch, env, ["reset-password", "--email", "x@y.z", "--password-stdin"], PASSWORD) == 1


def test_migrate_down_cli(monkeypatch, env):
    run(monkeypatch, env, ["migrate"])
    assert run(monkeypatch, env, ["migrate-down", "--steps", "4"]) == 0
    from app import migrate

    assert migrate.current_version(connect(env["JAPRI_DB_PATH"])) == 0


def test_app_refuses_to_start_on_pending_migrations(tmp_path):
    from app.config import Settings
    from app.main import create_app

    with pytest.raises(RuntimeError, match="migrate"):
        create_app(Settings(db_path=str(tmp_path / "kosong.db")))
