import pytest

from avrae_mcp_server.config import Settings


def test_settings_load_from_env(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    monkeypatch.setenv("AVRAE_BOT_USER_ID", "123")
    settings = Settings()
    assert settings.discord_bot_token == "token"
    assert settings.avrae_bot_user_id == 123
    assert settings.mcp_server_name == "avrae-discord-mcp"


def test_settings_require_avrae_id(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    monkeypatch.delenv("AVRAE_BOT_USER_ID", raising=False)
    with pytest.raises(ValueError, match="AVRAE_BOT_USER_ID"):
        Settings()
