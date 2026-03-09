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



def test_settings_load_public_mcp_options(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    monkeypatch.setenv("AVRAE_BOT_USER_ID", "123")
    monkeypatch.setenv("MCP_TRANSPORT", "streamable-http")
    monkeypatch.setenv("MCP_HOST", "0.0.0.0")
    monkeypatch.setenv("MCP_PORT", "9000")
    monkeypatch.setenv("MCP_API_KEY", "secret")
    monkeypatch.setenv("MCP_PUBLIC_BASE_URL", "https://mcp.example.com")

    settings = Settings()

    assert settings.mcp_transport == "streamable-http"
    assert settings.mcp_host == "0.0.0.0"
    assert settings.mcp_port == 9000
    assert settings.mcp_api_key == "secret"
    assert settings.mcp_public_base_url == "https://mcp.example.com"
