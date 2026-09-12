from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.entities import Telemetria, VehiculoConocido


class VehiculoConocidoRepository(Protocol):
    async def existe(self, vehiculo_id: UUID) -> bool: ...

    async def obtener(self, vehiculo_id: UUID) -> VehiculoConocido | None: ...

    async def registrar(self, vehiculo: VehiculoConocido) -> VehiculoConocido: ...


class TelemetriaRepository(Protocol):
    async def guardar(self, telemetria: Telemetria) -> Telemetria: ...

    async def obtener_mas_reciente(self, vehiculo_id: UUID) -> Telemetria | None: ...

    async def listar_historico(
        self,
        vehiculo_id: UUID,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Telemetria]: ...
