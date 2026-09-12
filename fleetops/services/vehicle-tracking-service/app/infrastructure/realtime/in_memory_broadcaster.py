from __future__ import annotations

import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID


class InMemoryBroadcaster:
    """Reparte payloads de telemetria a los suscriptores conectados por SSE.
    Vive solo en memoria del proceso: valido para un unico worker/instancia."""

    def __init__(self):
        self._suscriptores: dict[UUID, set[asyncio.Queue]] = defaultdict(set)

    async def publicar(self, vehiculo_id: UUID, payload: dict[str, Any]) -> None:
        for cola in list(self._suscriptores.get(vehiculo_id, ())):
            await cola.put(payload)

    @asynccontextmanager
    async def suscribirse(self, vehiculo_id: UUID):
        cola: asyncio.Queue = asyncio.Queue()
        self._suscriptores[vehiculo_id].add(cola)
        try:
            yield cola
        finally:
            self._suscriptores[vehiculo_id].discard(cola)
