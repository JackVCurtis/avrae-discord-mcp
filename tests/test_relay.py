import asyncio
from datetime import datetime, timezone

import pytest

from avrae_mcp_server.relay import AvraeRelay, AvraeTimeoutError


def test_format_command_with_and_without_args() -> None:
    relay = AvraeRelay(avrae_bot_user_id=1)
    assert relay.format_command("roll", "1d20") == "!roll 1d20"
    assert relay.format_command("check", "") == "!check"


def test_format_command_rejects_empty_command() -> None:
    relay = AvraeRelay(avrae_bot_user_id=1)
    with pytest.raises(ValueError, match="command"):
        relay.format_command("", "x")


def test_single_message_response() -> None:
    async def scenario() -> None:
        relay = AvraeRelay(avrae_bot_user_id=42, response_timeout_seconds=0.5, collection_window_seconds=0.05)
        sent: list[str] = []

        async def send(content: str) -> None:
            sent.append(content)
            await asyncio.sleep(0)

        async def emit() -> None:
            await asyncio.sleep(0.02)
            relay.handle_discord_message(
                author_id=42,
                channel_id=100,
                content="Result: Total 17",
                message_id=999,
                created_at=datetime.now(timezone.utc),
            )

        emit_task = asyncio.create_task(emit())
        result = await relay.execute(send=send, channel_id=100, command="roll", args="1d20")
        await emit_task

        assert sent == ["!roll 1d20"]
        assert result["raw_text"] == "Result: Total 17"
        assert len(result["fragments"]) == 1
        assert result["parsed"]["dice_total"] == 17
        assert result["metadata"]["channel_id"] == 100

    asyncio.run(scenario())


def test_multi_message_response() -> None:
    async def scenario() -> None:
        relay = AvraeRelay(avrae_bot_user_id=42, response_timeout_seconds=0.5, collection_window_seconds=0.08)

        async def send(_: str) -> None:
            await asyncio.sleep(0)

        async def emit() -> None:
            await asyncio.sleep(0.02)
            relay.handle_discord_message(42, 100, "Part one", 1, datetime.now(timezone.utc))
            await asyncio.sleep(0.02)
            relay.handle_discord_message(42, 100, "Part two", 2, datetime.now(timezone.utc))

        emit_task = asyncio.create_task(emit())
        result = await relay.execute(send=send, channel_id=100, command="check", args="dex")
        await emit_task

        assert result["raw_text"] == "Part one\nPart two"
        assert [f["message_id"] for f in result["fragments"]] == [1, 2]

    asyncio.run(scenario())


def test_timeout_behavior() -> None:
    async def scenario() -> None:
        relay = AvraeRelay(avrae_bot_user_id=42, response_timeout_seconds=0.05, collection_window_seconds=0.01)

        async def send(_: str) -> None:
            await asyncio.sleep(0)

        with pytest.raises(AvraeTimeoutError):
            await relay.execute(send=send, channel_id=100, command="roll", args="1d20")

    asyncio.run(scenario())


def test_overlapping_in_flight_requests() -> None:
    async def scenario() -> None:
        relay = AvraeRelay(avrae_bot_user_id=42, response_timeout_seconds=0.5, collection_window_seconds=0.05)

        async def send(_: str) -> None:
            await asyncio.sleep(0)

        first = asyncio.create_task(relay.execute(send=send, channel_id=100, command="roll", args="1d20"))
        second = asyncio.create_task(relay.execute(send=send, channel_id=100, command="roll", args="1d6"))

        await asyncio.sleep(0.02)
        relay.handle_discord_message(42, 100, "First response", 11, datetime.now(timezone.utc))
        await asyncio.sleep(0.02)
        relay.handle_discord_message(42, 100, "Second response", 12, datetime.now(timezone.utc))

        first_result = await first
        second_result = await second
        assert first_result["raw_text"] == "First response"
        assert second_result["raw_text"] == "Second response"

    asyncio.run(scenario())
