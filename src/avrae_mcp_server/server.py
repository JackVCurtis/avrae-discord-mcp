from __future__ import annotations

import asyncio
import logging
import sys
from dataclasses import dataclass
from typing import Any

import discord
import structlog
from mcp.server.fastmcp import FastMCP

from avrae_mcp_server.config import Settings


class DiscordConnectionError(RuntimeError):
    """Raised when Discord operations cannot be completed."""


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

    def __post_init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        self._connect_task: asyncio.Task[Any] | None = None
        self.log = structlog.get_logger("discord_lifecycle")

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


def create_server(settings: Settings) -> FastMCP:
    mcp = FastMCP(name=settings.mcp_server_name, version=settings.mcp_server_version)
    lifecycle = DiscordLifecycle(settings)
    log = structlog.get_logger("avrae_mcp_server")

    @mcp.tool()
    async def healthcheck() -> dict[str, str]:
        """Report MCP + Discord connection readiness."""

        status = "ready" if lifecycle.client.is_ready() else "starting"
        return {"status": status}

    @mcp.tool()
    async def send_discord_message(content: str, channel_id: int | None = None) -> dict[str, str | int]:
        """Send a message to a Discord channel through the puppet bot."""

        destination = channel_id or settings.discord_default_channel_id
        if not destination:
            raise ValueError("No destination channel set; provide channel_id or DISCORD_DEFAULT_CHANNEL_ID")

        result = await lifecycle.send_message(destination, content)
        return {"status": "ok", "channel_id": destination, "message": result}

    @mcp.tool()
    async def shutdown_discord() -> dict[str, str]:
        """Gracefully close Discord connection."""

        await lifecycle.stop()
        return {"status": "stopped"}

    log.info("mcp_tools_registered", tools=["healthcheck", "send_discord_message", "shutdown_discord"])
    return mcp


def main() -> None:
    try:
        settings = Settings()
        configure_logging(settings.log_level)
        log = structlog.get_logger("avrae_mcp_server")
        log.info("mcp_server_boot", name=settings.mcp_server_name, version=settings.mcp_server_version)

        server = create_server(settings)
        server.run()
    except Exception as exc:  # noqa: BLE001
        structlog.get_logger("avrae_mcp_server").exception("fatal_server_error", error=str(exc))
        raise


if __name__ == "__main__":
    main()
