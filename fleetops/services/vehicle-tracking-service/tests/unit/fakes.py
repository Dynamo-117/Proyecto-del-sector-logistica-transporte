from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.entities import Telemetria, VehiculoConocido


class FakeVehiculoConocidoRepository:
    def __init__(self):
        self._vehiculos: dict[UUID, VehiculoConocido] = {}

    async def existe(self, vehiculo_id: UUID) -> bool:
        return vehiculo_id in self._vehiculos

    async def obtener(self, vehiculo_id: UUID) -> VehiculoConocido | None:
        return self._vehiculos.get(vehiculo_id)

    async def registrar(self, vehiculo: VehiculoConocido) -> VehiculoConocido:
        self._vehiculos[vehiculo.id] = vehiculo
        return vehiculo


class FakeTelemetriaRepository:
    def __init__(self):
        self._registros: list[Telemetria] = []

    async def guardar(self, telemetria: Telemetria) -> Telemetria:
        self._registros.append(telemetria)
        return telemetria

    async def obtener_mas_reciente(self, vehiculo_id: UUID) -> Telemetria | None:
        registros = [r for r in self._registros if r.vehiculo_id == vehiculo_id]
        if not registros:
            return None
        return max(registros, key=lambda r: r.timestamp)

    async def listar_historico(
        self,
        vehiculo_id: UUID,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Telemetria]:
        registros = [r for r in self._registros if r.vehiculo_id == vehiculo_id]
        if desde is not None:
            registros = [r for r in registros if r.timestamp >= desde]
        if hasta is not None:
            registros = [r for r in registros if r.timestamp <= hasta]
        registros.sort(key=lambda r: r.timestamp, reverse=True)
        return registros[skip : skip + limit]


class FakeBroadcaster:
    def __init__(self):
        self.publicados: list[tuple[UUID, dict[str, Any]]] = []

    async def publicar(self, vehiculo_id: UUID, payload: dict[str, Any]) -> None:
        self.publicados.append((vehiculo_id, payload))

    @asynccontextmanager
    async def suscribirse(self, vehiculo_id: UUID):
        yield None
