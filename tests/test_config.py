from avrae_mcp_server.config import Settings


def test_settings_load_from_env(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    settings = Settings()
    assert settings.discord_bot_token == "token"
    assert settings.mcp_server_name == "avrae-discord-mcp"
