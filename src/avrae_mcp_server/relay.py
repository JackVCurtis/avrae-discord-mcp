from __future__ import annotations

import asyncio
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Awaitable, Callable


class AvraeTimeoutError(TimeoutError):
    """Raised when Avrae does not respond before timeout."""


@dataclass
class ResponseFragment:
    message_id: int
    content: str
    timestamp: str


@dataclass
class PendingRequest:
    request_id: str
    channel_id: int
    started_at_monotonic: float
    first_response_event: asyncio.Event = field(default_factory=asyncio.Event)
    fragments: list[ResponseFragment] = field(default_factory=list)


class AvraeRelay:
    def __init__(
        self,
        avrae_bot_user_id: int,
        response_timeout_seconds: float = 8.0,
        collection_window_seconds: float = 0.25,
        max_collected_messages: int = 6,
    ) -> None:
        self.avrae_bot_user_id = avrae_bot_user_id
        self.response_timeout_seconds = response_timeout_seconds
        self.collection_window_seconds = collection_window_seconds
        self.max_collected_messages = max_collected_messages
        self._pending_by_channel: dict[int, list[PendingRequest]] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def format_command(command: str, args: str) -> str:
        trimmed_command = command.strip()
        if not trimmed_command:
            raise ValueError("command is required")

        trimmed_args = args.strip()
        if len(trimmed_command) > 64:
            raise ValueError("command is too long")
        if len(trimmed_args) > 1800:
            raise ValueError("args is too long")

        return f"!{trimmed_command} {trimmed_args}".strip()

    async def execute(
        self,
        send: Callable[[str], Awaitable[None]],
        channel_id: int,
        command: str,
        args: str,
    ) -> dict[str, object]:
        request = PendingRequest(
            request_id=str(uuid.uuid4()),
            channel_id=channel_id,
            started_at_monotonic=time.monotonic(),
        )

        async with self._lock:
            self._pending_by_channel.setdefault(channel_id, []).append(request)

        payload = self.format_command(command, args)
        await send(payload)

        try:
            await asyncio.wait_for(request.first_response_event.wait(), timeout=self.response_timeout_seconds)
        except asyncio.TimeoutError as exc:
            await self._remove_pending(request)
            raise AvraeTimeoutError(f"No Avrae response before timeout ({self.response_timeout_seconds}s)") from exc

        await asyncio.sleep(self.collection_window_seconds)
        await self._remove_pending(request)

        raw_text = "\n".join(fragment.content for fragment in request.fragments)
        parsed_total = self._parse_dice_total(raw_text)
        first_message_id = request.fragments[0].message_id if request.fragments else None

        return {
            "raw_text": raw_text,
            "fragments": [fragment.__dict__ for fragment in request.fragments],
            "parsed": {"dice_total": parsed_total},
            "metadata": {
                "request_id": request.request_id,
                "channel_id": channel_id,
                "message_id": first_message_id,
                "latency_ms": int((time.monotonic() - request.started_at_monotonic) * 1000),
            },
        }

    async def _remove_pending(self, request: PendingRequest) -> None:
        async with self._lock:
            channel_pending = self._pending_by_channel.get(request.channel_id, [])
            self._pending_by_channel[request.channel_id] = [item for item in channel_pending if item.request_id != request.request_id]
            if not self._pending_by_channel[request.channel_id]:
                self._pending_by_channel.pop(request.channel_id, None)

    def handle_discord_message(
        self,
        author_id: int,
        channel_id: int,
        content: str,
        message_id: int,
        created_at: datetime,
    ) -> bool:
        if author_id != self.avrae_bot_user_id:
            return False

        pending_requests = self._pending_by_channel.get(channel_id, [])
        if not pending_requests:
            return False

        active_request = next((item for item in pending_requests if not item.fragments), pending_requests[0])
        if len(active_request.fragments) >= self.max_collected_messages:
            return True

        active_request.fragments.append(
            ResponseFragment(
                message_id=message_id,
                content=content,
                timestamp=created_at.isoformat(),
            )
        )
        active_request.first_response_event.set()
        return True

    @staticmethod
    def _parse_dice_total(raw_text: str) -> int | None:
        match = re.search(r"(?i)total\D*(-?\d+)", raw_text)
        if not match:
            return None
        return int(match.group(1))
