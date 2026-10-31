"""CIVORA Real-time Event Streaming and SSE Broadcaster.

Allows Web UI clients to subscribe to live agent thoughts, tool calls,
execution logs, and verification stages via Server-Sent Events (SSE).
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, List, Optional


@dataclass
class AgentEvent:
    event_type: str  # step | tool_call | tool_result | log | finding | patch | verification | status
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    def to_sse(self) -> str:
        payload = json.dumps({
            "event": self.event_type,
            "timestamp": self.timestamp,
            "data": self.data,
        })
        return f"data: {payload}\n\n"


class EventBroadcaster:
    """Manages active SSE subscriber queues per task."""

    def __init__(self):
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, task_id: str) -> asyncio.Queue:
        q = asyncio.Queue()
        if task_id not in self._subscribers:
            self._subscribers[task_id] = []
        self._subscribers[task_id].append(q)
        return q

    def unsubscribe(self, task_id: str, queue: asyncio.Queue) -> None:
        if task_id in self._subscribers:
            self._subscribers[task_id] = [q for q in self._subscribers[task_id] if q is not queue]
            if not self._subscribers[task_id]:
                del self._subscribers[task_id]

    async def emit(self, task_id: str, event_type: str, data: Dict[str, Any]) -> None:
        event = AgentEvent(event_type=event_type, data=data)
        if task_id in self._subscribers:
            for q in list(self._subscribers[task_id]):
                await q.put(event)

    async def event_generator(self, task_id: str) -> AsyncGenerator[str, None]:
        q = self.subscribe(task_id)
        try:
            # Yield initial connection heartbeat
            yield AgentEvent(event_type="connected", data={"task_id": task_id}).to_sse()
            while True:
                try:
                    event: AgentEvent = await asyncio.wait_for(q.get(), timeout=30.0)
                    yield event.to_sse()
                    if event.event_type in ("status", "task_completed") and event.data.get("status") in ("VERIFIED", "FAILED", "ABORTED", "COMPLETED"):
                        break
                except asyncio.TimeoutError:
                    # Keepalive ping
                    yield ": ping\n\n"
        finally:
            self.unsubscribe(task_id, q)

