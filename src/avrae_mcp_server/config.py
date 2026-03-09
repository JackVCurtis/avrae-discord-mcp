from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    discord_bot_token: str = Field(..., alias="DISCORD_BOT_TOKEN")
    discord_guild_id: int | None = Field(default=None, alias="DISCORD_GUILD_ID")
    discord_default_channel_id: int | None = Field(default=None, alias="DISCORD_DEFAULT_CHANNEL_ID")

    mcp_server_name: str = Field(default="avrae-discord-mcp", alias="MCP_SERVER_NAME")
    mcp_server_version: str = Field(default="0.1.0", alias="MCP_SERVER_VERSION")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
