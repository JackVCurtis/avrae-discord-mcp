import os


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        self.discord_bot_token = self._require("DISCORD_BOT_TOKEN")
        self.avrae_bot_user_id = self._parse_required_int("AVRAE_BOT_USER_ID")
        self.discord_guild_id = self._parse_optional_int("DISCORD_GUILD_ID")
        self.discord_application_id = self._parse_optional_int("DISCORD_APPLICATION_ID")
        self.discord_default_channel_id = self._parse_optional_int("DISCORD_DEFAULT_CHANNEL_ID")
        self.default_thread_id = self._parse_optional_int("DEFAULT_THREAD_ID")
        self.response_timeout_seconds = self._parse_optional_float("RESPONSE_TIMEOUT_SECONDS", 8.0)
        self.max_collected_messages = self._parse_optional_int("MAX_COLLECTED_MESSAGES") or 6
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
    def _parse_required_int(env_var: str) -> int:
        value = Settings._require(env_var)
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"{env_var} must be an integer") from exc

    @staticmethod
    def _parse_optional_int(env_var: str) -> int | None:
        value = os.getenv(env_var)
        if value is None or value == "":
            return None

        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"{env_var} must be an integer") from exc

    @staticmethod
    def _parse_optional_float(env_var: str, default: float) -> float:
        value = os.getenv(env_var)
        if value is None or value == "":
            return default
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"{env_var} must be a number") from exc
