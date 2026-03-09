import pytest
import asyncio
import importlib
import sys
from types import ModuleType, SimpleNamespace


class FakeMCP:
    def __init__(self, name: str, version: str, **kwargs):
        self.name = name
        self.version = version
        self.tools = {}
        self.kwargs = kwargs
        self.run_calls = []

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator

    def run(self, transport: str = "stdio", mount_path: str | None = None):
        self.run_calls.append({"transport": transport, "mount_path": mount_path})


class FakeLifecycle:
    def __init__(self):
        self.client = SimpleNamespace(is_ready=lambda: True)
        self.sent = []

    async def send_message(self, channel_id: int, content: str) -> None:
        self.sent.append((channel_id, content))

    async def stop(self) -> None:
        return None


class FakeRelay:
    async def execute(self, send, channel_id: int, command: str, args: str):
        await send(f"!{command} {args}".strip())
        return {"raw_text": "ok", "fragments": [], "parsed": {"dice_total": None}, "metadata": {"channel_id": channel_id}}


def _install_fake_dependencies() -> None:
    discord_module = ModuleType("discord")
    discord_module.Intents = SimpleNamespace(default=lambda: SimpleNamespace(message_content=True))
    discord_module.Client = lambda intents=None: SimpleNamespace(event=lambda fn: fn, is_ready=lambda: True)
    discord_module.Message = object
    sys.modules["discord"] = discord_module

    mcp_module = ModuleType("mcp")
    mcp_server_module = ModuleType("mcp.server")
    fastmcp_module = ModuleType("mcp.server.fastmcp")
    auth_module = ModuleType("mcp.server.auth")
    auth_provider_module = ModuleType("mcp.server.auth.provider")
    auth_settings_module = ModuleType("mcp.server.auth.settings")

    class AccessToken:
        def __init__(self, *, token: str, client_id: str, scopes: list[str], expires_at=None, resource=None):
            self.token = token
            self.client_id = client_id
            self.scopes = scopes
            self.expires_at = expires_at
            self.resource = resource

    class AuthSettings:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fastmcp_module.FastMCP = FakeMCP
    auth_provider_module.AccessToken = AccessToken
    auth_settings_module.AuthSettings = AuthSettings

    sys.modules["mcp"] = mcp_module
    sys.modules["mcp.server"] = mcp_server_module
    sys.modules["mcp.server.fastmcp"] = fastmcp_module
    sys.modules["mcp.server.auth"] = auth_module
    sys.modules["mcp.server.auth.provider"] = auth_provider_module
    sys.modules["mcp.server.auth.settings"] = auth_settings_module

    structlog_module = ModuleType("structlog")
    structlog_module.get_logger = lambda *args, **kwargs: SimpleNamespace(info=lambda *a, **k: None, exception=lambda *a, **k: None)
    structlog_module.configure = lambda *args, **kwargs: None
    structlog_module.processors = SimpleNamespace(TimeStamper=lambda fmt=None: None, format_exc_info=None, JSONRenderer=lambda: None)
    structlog_module.stdlib = SimpleNamespace(add_log_level=None, LoggerFactory=lambda: None)
    sys.modules["structlog"] = structlog_module


def test_create_server_registers_expected_tools(monkeypatch):
    _install_fake_dependencies()
    server_module = importlib.import_module("avrae_mcp_server.server")
    server_module = importlib.reload(server_module)

    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    monkeypatch.setenv("AVRAE_BOT_USER_ID", "42")
    monkeypatch.setenv("DISCORD_DEFAULT_CHANNEL_ID", "100")

    from avrae_mcp_server.config import Settings

    settings = Settings()
    lifecycle = FakeLifecycle()
    relay = FakeRelay()

    server = server_module.create_server(settings=settings, lifecycle=lifecycle, relay=relay)
    expected_core_tools = {"healthcheck", "avrae_command", "shutdown_discord"}
    expected_command_tools = {
        "avrae_randchar",
        "avrae_randname",
        "avrae_rollstats",
        "avrae_about",
        "avrae_changelog",
        "avrae_ddb",
        "avrae_invite",
        "avrae_ping",
        "avrae_alias",
        "avrae_cvar",
        "avrae_globalvar",
        "avrae_multiline",
        "avrae_prefix",
        "avrae_servalias",
        "avrae_server_settings",
        "avrae_servervar",
        "avrae_servsnippet",
        "avrae_snippet",
        "avrae_tembed",
        "avrae_test",
        "avrae_uservar",
        "avrae_iterroll",
        "avrae_monattack",
        "avrae_moncast",
        "avrae_moncheck",
        "avrae_monsave",
        "avrae_multiroll",
        "avrae_roll",
        "avrae_campaign",
        "avrae_cast",
        "avrae_customcounter",
        "avrae_game",
        "avrae_spellbook",
        "avrae_bestiary",
        "avrae_pack",
        "avrae_tome",
        "avrae_init",
        "avrae_background",
        "avrae_class",
        "avrae_classfeat",
        "avrae_condition",
        "avrae_feat",
        "avrae_item",
        "avrae_monimage",
        "avrae_monster",
        "avrae_race",
        "avrae_racefeat",
        "avrae_rule",
        "avrae_spell",
        "avrae_subclass",
        "avrae_token",
        "avrae_br",
        "avrae_echo",
        "avrae_embed",
        "avrae_techo",
        "avrae_action",
        "avrae_character",
        "avrae_check",
        "avrae_csettings",
        "avrae_desc",
        "avrae_import",
        "avrae_portrait",
        "avrae_save",
        "avrae_sheet",
        "avrae_transferchar",
        "avrae_update",
        "avrae_help",
        "avrae_tutorial",
    }
    assert set(server.tools) == expected_core_tools | expected_command_tools

    result = asyncio.run(server.tools["avrae_command"]("roll", "1d20"))
    assert lifecycle.sent == [(100, "!roll 1d20")]
    assert result["metadata"]["channel_id"] == 100

    command_result = asyncio.run(server.tools["avrae_roll"]("2d20kh1"))
    assert lifecycle.sent[-1] == (100, "!roll 2d20kh1")
    assert command_result["metadata"]["channel_id"] == 100


def test_create_server_enables_api_key_verification_when_configured(monkeypatch):
    _install_fake_dependencies()
    server_module = importlib.import_module("avrae_mcp_server.server")
    server_module = importlib.reload(server_module)

    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    monkeypatch.setenv("AVRAE_BOT_USER_ID", "42")
    monkeypatch.setenv("MCP_API_KEY", "secret")
    monkeypatch.setenv("MCP_PUBLIC_BASE_URL", "https://mcp.example.com")

    from avrae_mcp_server.config import Settings

    settings = Settings()
    server = server_module.create_server(settings=settings, lifecycle=FakeLifecycle(), relay=FakeRelay())
    token_verifier = server.kwargs["token_verifier"]

    valid_token = asyncio.run(token_verifier.verify_token("secret"))
    invalid_token = asyncio.run(token_verifier.verify_token("bad"))

    assert valid_token is not None
    assert valid_token.scopes == ["mcp:access"]
    assert invalid_token is None



def test_create_server_requires_public_base_url_with_api_key(monkeypatch):
    _install_fake_dependencies()
    server_module = importlib.import_module("avrae_mcp_server.server")
    server_module = importlib.reload(server_module)

    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token")
    monkeypatch.setenv("AVRAE_BOT_USER_ID", "42")
    monkeypatch.setenv("MCP_API_KEY", "secret")
    monkeypatch.delenv("MCP_PUBLIC_BASE_URL", raising=False)

    from avrae_mcp_server.config import Settings

    settings = Settings()

    with pytest.raises(ValueError, match="MCP_PUBLIC_BASE_URL"):
        server_module.create_server(settings=settings, lifecycle=FakeLifecycle(), relay=FakeRelay())
