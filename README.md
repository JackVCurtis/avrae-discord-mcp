# avrae-discord-mcp

An MCP server for interacting with the Avrae.io Discord bot through a user-hosted Discord bot.

## Updated architecture assumptions

This project is designed for **private/self-hosted use**:

- The MCP user brings their own Discord bot token.
- The MCP user configures their own Discord webhook endpoint.
- The server is not intended for public multi-tenant hosting.

Because of this, the design prioritizes reliability and command fidelity over heavy abuse-prevention layers.

## MVP integration plan

### 1) Server scaffold

- Build a minimal MCP server process that exposes Avrae-facing tools.
- Add a Discord client relay service that can post messages to a configured channel/thread.
- Add an async event listener for Avrae replies.

### 2) Tool interface that mirrors Avrae commands

Expose a generic tool first:

- `avrae_command(command: string, args: string, context?: object)`

This allows agents to call Avrae exactly as they would in Discord (`!roll`, `!check`, etc.) while preserving flexibility.

Optional future enhancement:

- Generate command-specific tools from a command catalog for stronger type safety.

### 3) Request/response relay flow

1. MCP tool call arrives with command + arguments.
2. Server formats and sends a Discord message through the user bot into configured channel/thread.
3. Server listens for Avrae bot response messages.
4. Response is correlated to the MCP request by channel, time window, and request ID state.
5. MCP returns both raw Avrae text and metadata (`channel_id`, `message_id`, latency).

### 4) Configuration model

Use local config/env vars for:

- `DISCORD_BOT_TOKEN`
- `AVRAE_BOT_USER_ID`
- `DEFAULT_GUILD_ID`
- `DEFAULT_CHANNEL_ID`
- optional `DEFAULT_THREAD_ID`
- webhook URL/credentials if webhook path is used
- response timeout and max collected messages

### 5) Reliability controls (instead of heavy abuse controls)

Given private deployment assumptions, keep controls lightweight:

- command timeout + clear timeout errors
- basic input length validation
- optional channel allowlist (small, user-managed)
- structured logs with request IDs
- retry/backoff for transient Discord send failures

### 6) Response shaping

Return:

- raw concatenated Avrae response text
- per-message fragments (for multi-message responses)
- parsed fields when possible (dice totals, roll breakdowns)
- correlation metadata and timestamps

### 7) Testing strategy

- Unit tests for command formatting and response correlation.
- Async tests with mocked Discord events for:
  - single-message reply
  - multi-message reply
  - timeout behavior
  - overlapping in-flight requests
- Minimal smoke test for MCP tool registration.

## Initial milestone checklist

- [ ] Basic MCP server boots and registers `avrae_command`.
- [ ] Discord bot can post command text into configured channel.
- [ ] Avrae response is captured and returned to MCP caller.
- [ ] Timeout and error responses are deterministic.
- [ ] Unit + async integration tests pass locally.

## Development setup

Install dependencies and run tests locally:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pytest
```
