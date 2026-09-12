from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.application.ports.realtime import RealtimeBroadcaster
from app.application.ports.repositories import TelemetriaRepository, VehiculoConocidoRepository
from app.domain.entities import Telemetria
from app.domain.exceptions import TelemetriaNoDisponible, VehiculoDesconocido


class IngestarTelemetria:
    def __init__(
        self,
        telemetria_repo: TelemetriaRepository,
        vehiculo_repo: VehiculoConocidoRepository,
        broadcaster: RealtimeBroadcaster,
    ):
        self._telemetria_repo = telemetria_repo
        self._vehiculo_repo = vehiculo_repo
        self._broadcaster = broadcaster

    async def ejecutar(
        self,
        vehiculo_id: UUID,
        latitud: float,
        longitud: float,
        velocidad_kmh: float,
        timestamp: datetime | None = None,
    ) -> Telemetria:
        if not await self._vehiculo_repo.existe(vehiculo_id):
            raise VehiculoDesconocido(
                f"Vehiculo '{vehiculo_id}' no esta registrado en vehicle-tracking-service"
            )

        kwargs = {"timestamp": timestamp} if timestamp is not None else {}
        telemetria = Telemetria(
            vehiculo_id=vehiculo_id,
            latitud=latitud,
            longitud=longitud,
            velocidad_kmh=velocidad_kmh,
            **kwargs,
        )
        telemetria = await self._telemetria_repo.guardar(telemetria)

        await self._broadcaster.publicar(
            vehiculo_id,
            {
                "vehiculo_id": str(telemetria.vehiculo_id),
                "latitud": telemetria.latitud,
                "longitud": telemetria.longitud,
                "velocidad_kmh": telemetria.velocidad_kmh,
                "estado_movimiento": telemetria.estado_movimiento.value,
                "timestamp": telemetria.timestamp.isoformat(),
            },
        )
        return telemetria


class ObtenerEstadoActual:
    def __init__(
        self, telemetria_repo: TelemetriaRepository, vehiculo_repo: VehiculoConocidoRepository
    ):
        self._telemetria_repo = telemetria_repo
        self._vehiculo_repo = vehiculo_repo

    async def ejecutar(self, vehiculo_id: UUID) -> Telemetria:
        if not await self._vehiculo_repo.existe(vehiculo_id):
            raise VehiculoDesconocido(
                f"Vehiculo '{vehiculo_id}' no esta registrado en vehicle-tracking-service"
            )

        telemetria = await self._telemetria_repo.obtener_mas_reciente(vehiculo_id)
        if telemetria is None:
            raise TelemetriaNoDisponible(f"Aun no hay telemetria registrada para '{vehiculo_id}'")
        return telemetria


class ListarHistoricoTelemetria:
    def __init__(
        self, telemetria_repo: TelemetriaRepository, vehiculo_repo: VehiculoConocidoRepository
    ):
        self._telemetria_repo = telemetria_repo
        self._vehiculo_repo = vehiculo_repo

    async def ejecutar(
        self,
        vehiculo_id: UUID,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Telemetria]:
        if not await self._vehiculo_repo.existe(vehiculo_id):
            raise VehiculoDesconocido(
                f"Vehiculo '{vehiculo_id}' no esta registrado en vehicle-tracking-service"
            )

        return await self._telemetria_repo.listar_historico(
            vehiculo_id, desde=desde, hasta=hasta, skip=skip, limit=limit
        )
