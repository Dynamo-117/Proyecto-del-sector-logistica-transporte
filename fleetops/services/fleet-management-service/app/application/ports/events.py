from __future__ import annotations

from typing import Any, Protocol


class EventPublisher(Protocol):
    async def publicar(self, routing_key: str, payload: dict[str, Any]) -> None: ...
