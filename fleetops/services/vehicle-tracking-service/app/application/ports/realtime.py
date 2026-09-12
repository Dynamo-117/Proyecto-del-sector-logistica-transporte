from __future__ import annotations

import asyncio
from contextlib import AbstractAsyncContextManager
from typing import Any, Protocol
from uuid import UUID


class RealtimeBroadcaster(Protocol):
    async def publicar(self, vehiculo_id: UUID, payload: dict[str, Any]) -> None: ...

    def suscribirse(self, vehiculo_id: UUID) -> AbstractAsyncContextManager[asyncio.Queue]: ...
