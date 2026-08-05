# ruff: file-ignore[hardcoded-password-string]
from typing import TYPE_CHECKING

from glitchtip_jira_bridge.config import SECRETS_DIR, Settings, resolve_secrets_dir

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_resolve_secrets_dir_returns_path_when_directory_exists(
    tmp_path: Path,
) -> None:
    assert resolve_secrets_dir(tmp_path) == tmp_path


def test_resolve_secrets_dir_returns_none_when_directory_missing(
    tmp_path: Path,
) -> None:
    assert resolve_secrets_dir(tmp_path / "does-not-exist") is None


def test_settings_secrets_dir_is_wired_to_resolved_path() -> None:
    assert Settings.model_config.get("secrets_dir") == resolve_secrets_dir(SECRETS_DIR)


def test_settings_reads_secret_from_secrets_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "gjb_jira_api_token").write_text("file-token")
    monkeypatch.setitem(Settings.model_config, "secrets_dir", tmp_path)
    monkeypatch.delenv("GJB_JIRA_API_TOKEN", raising=False)

    assert Settings().jira_api_token == "file-token"


def test_settings_env_var_overrides_secrets_dir_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "gjb_jira_api_token").write_text("file-token")
    monkeypatch.setitem(Settings.model_config, "secrets_dir", tmp_path)
    monkeypatch.setenv("GJB_JIRA_API_TOKEN", "env-token")

    assert Settings().jira_api_token == "env-token"
