import os


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        self.discord_bot_token = self._require("DISCORD_BOT_TOKEN")
        self.discord_guild_id = self._parse_optional_int("DISCORD_GUILD_ID")
        self.discord_default_channel_id = self._parse_optional_int("DISCORD_DEFAULT_CHANNEL_ID")
        self.mcp_server_name = os.getenv("MCP_SERVER_NAME", "avrae-discord-mcp")
        self.mcp_server_version = os.getenv("MCP_SERVER_VERSION", "0.1.0")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def _require(env_var: str) -> str:
        value = os.getenv(env_var)
        if not value:
            raise ValueError(f"{env_var} is required")
        return value

    @staticmethod
    def _parse_optional_int(env_var: str) -> int | None:
        value = os.getenv(env_var)
        if value is None or value == "":
            return None

        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"{env_var} must be an integer") from exc
