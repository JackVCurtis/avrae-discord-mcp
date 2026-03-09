from __future__ import annotations

import asyncio
import logging
import sys
from dataclasses import dataclass
from datetime import timezone
from typing import Any

import discord
from discord import Permissions
import structlog
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP

from avrae_mcp_server.config import Settings
from avrae_mcp_server.relay import AvraeRelay, AvraeTimeoutError


TOP_LEVEL_COMMANDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("randchar", ()),
    ("randname", ("name",)),
    ("rollstats", ()),
    ("about", ("stats", "info")),
    ("changelog", ()),
    ("ddb", ()),
    ("invite", ()),
    ("ping", ()),
    ("alias", ()),
    ("cvar", ()),
    ("globalvar", ("gvar",)),
    ("multiline", ()),
    ("prefix", ()),
    ("servalias", ("serveralias",)),
    ("server_settings", ("servsettings",)),
    ("servervar", ("svar",)),
    ("servsnippet", ("serversnippet",)),
    ("snippet", ()),
    ("tembed", ()),
    ("test", ()),
    ("uservar", ("uvar",)),
    ("iterroll", ("rrr",)),
    ("monattack", ("ma", "monster_attack")),
    ("moncast", ("mcast", "monster_cast")),
    ("moncheck", ("mc", "monster_check")),
    ("monsave", ("ms", "monster_save")),
    ("multiroll", ("rr",)),
    ("roll", ("r",)),
    ("campaign", ()),
    ("cast", ()),
    ("customcounter", ("cc",)),
    ("game", ("g",)),
    ("spellbook", ("sb",)),
    ("bestiary", ()),
    ("pack", ()),
    ("tome", ()),
    ("init", ("i", "I")),
    ("background", ()),
    ("class", ()),
    ("classfeat", ()),
    ("condition", ("status",)),
    ("feat", ()),
    ("item", ()),
    ("monimage", ()),
    ("monster", ()),
    ("race", ("species",)),
    ("racefeat", ("speciesfeat",)),
    ("rule", ("reference",)),
    ("spell", ()),
    ("subclass", ()),
    ("token", ()),
    ("br", ()),
    ("echo", ()),
    ("embed", ()),
    ("techo", ()),
    ("action", ("a", "attack")),
    ("character", ("char",)),
    ("check", ("c",)),
    ("csettings", ()),
    ("desc", ()),
    ("import", ()),
    ("portrait", ()),
    ("save", ("s",)),
    ("sheet", ()),
    ("transferchar", ()),
    ("update", ()),
    ("help", ()),
    ("tutorial", ()),
)


class ApiKeyTokenVerifier:
    """Validate MCP bearer tokens against a single configured API key."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    async def verify_token(self, token: str) -> AccessToken | None:
        if token != self._api_key:
            return None

        return AccessToken(
            token=token,
            client_id="api-key-client",
            scopes=["mcp:access"],
        )


def _build_fastmcp_kwargs(settings: Settings) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "host": settings.mcp_host,
        "port": settings.mcp_port,
    }

    if settings.mcp_api_key:
        if not settings.mcp_public_base_url:
            raise ValueError("MCP_PUBLIC_BASE_URL is required when MCP_API_KEY is set")

        public_base = settings.mcp_public_base_url.rstrip("/")
        kwargs["token_verifier"] = ApiKeyTokenVerifier(settings.mcp_api_key)
        kwargs["auth"] = AuthSettings(
            issuer_url=f"{public_base}/",
            resource_server_url=f"{public_base}/mcp",
            required_scopes=["mcp:access"],
        )

    return kwargs


class DiscordConnectionError(RuntimeError):
    """Raised when Discord operations cannot be completed."""




def build_creator_install_url(application_id: int) -> str:
    """Build a public Discord OAuth2 URL that allows the creator to install the bot."""

    return discord.utils.oauth_url(
        client_id=application_id,
        permissions=Permissions(
            send_messages=True,
            read_message_history=True,
            view_channel=True,
        ),
        scopes=("bot", "applications.commands"),
    )


def configure_logging(level: str) -> None:
    """Configure structured JSON logging for MCP and Discord events."""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        stream=sys.stdout,
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


@dataclass
class DiscordLifecycle:
    settings: Settings
    relay: AvraeRelay

    def __post_init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        self._connect_task: asyncio.Task[Any] | None = None
        self.log = structlog.get_logger("discord_lifecycle")

        @self.client.event
        async def on_message(message: discord.Message) -> None:
            self.relay.handle_discord_message(
                author_id=message.author.id,
                channel_id=message.channel.id,
                content=message.content,
                message_id=message.id,
                created_at=message.created_at.astimezone(timezone.utc),
            )

    async def start(self) -> None:
        if self.client.is_ready() or self._connect_task:
            return

        try:
            await self.client.login(self.settings.discord_bot_token)
            self._connect_task = asyncio.create_task(self.client.connect(reconnect=True))
            self.log.info("discord_connect_started")
        except Exception as exc:  # noqa: BLE001
            self.log.exception("discord_connect_failed", error=str(exc))
            raise DiscordConnectionError("Failed to connect to Discord") from exc

    async def stop(self) -> None:
        try:
            await self.client.close()
            if self._connect_task:
                await self._connect_task
        except Exception as exc:  # noqa: BLE001
            self.log.exception("discord_shutdown_failed", error=str(exc))

    async def send_message(self, channel_id: int, content: str) -> str:
        await self.start()
        try:
            channel = self.client.get_channel(channel_id) or await self.client.fetch_channel(channel_id)
            await channel.send(content)
            self.log.info("discord_message_sent", channel_id=channel_id)
            return f"Message sent to channel {channel_id}."
        except Exception as exc:  # noqa: BLE001
            self.log.exception("discord_message_failed", channel_id=channel_id, error=str(exc))
            raise DiscordConnectionError(f"Failed to send Discord message: {exc}") from exc


def create_server(settings: Settings, lifecycle: DiscordLifecycle | None = None, relay: AvraeRelay | None = None) -> FastMCP:
    mcp = FastMCP(
        name=settings.mcp_server_name,
        version=settings.mcp_server_version,
        **_build_fastmcp_kwargs(settings),
    )
    relay = relay or AvraeRelay(
        avrae_bot_user_id=settings.avrae_bot_user_id,
        response_timeout_seconds=settings.response_timeout_seconds,
        max_collected_messages=settings.max_collected_messages,
    )
    lifecycle = lifecycle or DiscordLifecycle(settings=settings, relay=relay)
    log = structlog.get_logger("avrae_mcp_server")

    @mcp.tool()
    async def healthcheck() -> dict[str, str]:
        """Report MCP + Discord connection readiness."""

        status = "ready" if lifecycle.client.is_ready() else "starting"
        return {"status": status}

    @mcp.tool()
    async def avrae_command(command: str, args: str = "", context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send an Avrae command and return correlated response payload."""

        destination = (context or {}).get("channel_id") or settings.discord_default_channel_id
        if not destination:
            raise ValueError("No destination channel set; provide context.channel_id or DISCORD_DEFAULT_CHANNEL_ID")

        try:
            return await relay.execute(
                send=lambda content: lifecycle.send_message(int(destination), content),
                channel_id=int(destination),
                command=command,
                args=args,
            )
        except AvraeTimeoutError as exc:
            return {"error": "timeout", "detail": str(exc), "channel_id": int(destination)}

    @mcp.tool()
    async def shutdown_discord() -> dict[str, str]:
        """Gracefully close Discord connection."""

        await lifecycle.stop()
        return {"status": "stopped"}

    @mcp.tool()
    async def creator_install_url() -> dict[str, str]:
        """Return a public Discord OAuth2 URL that the app creator can use to install this bot."""

        application_id = settings.discord_application_id
        if not application_id:
            raise ValueError("DISCORD_APPLICATION_ID is required to generate an install URL")

        return {"install_url": build_creator_install_url(application_id)}

    def normalize_tool_name(command: str) -> str:
        normalized = command.replace("-", "_").replace(" ", "_")
        if not normalized.isidentifier():
            normalized = f"command_{normalized}"
        return f"avrae_{normalized}"

    registered_tools = ["healthcheck", "avrae_command", "shutdown_discord", "creator_install_url"]

    for command, aliases in TOP_LEVEL_COMMANDS:
        async def command_tool(args: str = "", context: dict[str, Any] | None = None, _command: str = command) -> dict[str, Any]:
            """Send a specific top-level Avrae command with optional raw argument text."""

            return await avrae_command(command=_command, args=args, context=context)

        command_tool.__name__ = normalize_tool_name(command)
        alias_text = ", ".join(f"!{alias}" for alias in aliases)
        command_tool.__doc__ = (
            f"Shortcut for !{command}."
            if not alias_text
            else f"Shortcut for !{command} (aliases: {alias_text})."
        )
        mcp.tool()(command_tool)
        registered_tools.append(command_tool.__name__)

    log.info("mcp_tools_registered", tools=registered_tools)
    return mcp


def main() -> None:
    try:
        settings = Settings()
        configure_logging(settings.log_level)
        log = structlog.get_logger("avrae_mcp_server")
        log.info("mcp_server_boot", name=settings.mcp_server_name, version=settings.mcp_server_version)

        server = create_server(settings)
        server.run(transport=settings.mcp_transport)
    except Exception as exc:  # noqa: BLE001
        structlog.get_logger("avrae_mcp_server").exception("fatal_server_error", error=str(exc))
        raise


if __name__ == "__main__":
    main()
