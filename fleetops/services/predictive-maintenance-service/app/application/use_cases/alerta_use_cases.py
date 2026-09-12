from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.application.ports.repositories import (
    AlertaRepository,
    EstadoMantenimientoRepository,
    LecturaOdometroRepository,
    VehiculoConocidoRepository,
)
from app.domain.entities import Alerta, EstadoAlerta
from app.domain.exceptions import AlertaNoEncontrada, AlertaYaResuelta, VehiculoDesconocido


class ListarAlertasActivas:
    def __init__(self, alerta_repo: AlertaRepository, vehiculo_repo: VehiculoConocidoRepository):
        self._alerta_repo = alerta_repo
        self._vehiculo_repo = vehiculo_repo

    async def ejecutar(self, vehiculo_id: UUID) -> list[Alerta]:
        if not await self._vehiculo_repo.existe(vehiculo_id):
            raise VehiculoDesconocido(
                f"Vehiculo '{vehiculo_id}' no esta registrado en predictive-maintenance-service"
            )
        return await self._alerta_repo.listar_por_vehiculo(vehiculo_id, EstadoAlerta.ACTIVA)


class MarcarMantenimientoRealizado:
    """Resuelve la alerta y desplaza la referencia (km/horas base) de ese tipo
    de mantenimiento hasta la lectura mas reciente del vehiculo, para que el
    proximo umbral se cuente desde este momento."""

    def __init__(
        self,
        alerta_repo: AlertaRepository,
        estado_repo: EstadoMantenimientoRepository,
        lectura_repo: LecturaOdometroRepository,
    ):
        self._alerta_repo = alerta_repo
        self._estado_repo = estado_repo
        self._lectura_repo = lectura_repo

    async def ejecutar(self, alerta_id: UUID) -> Alerta:
        alerta = await self._alerta_repo.obtener(alerta_id)
        if alerta is None:
            raise AlertaNoEncontrada(f"Alerta '{alerta_id}' no encontrada")
        if alerta.estado == EstadoAlerta.RESUELTA:
            raise AlertaYaResuelta(f"Alerta '{alerta_id}' ya fue resuelta")

        alerta.estado = EstadoAlerta.RESUELTA
        alerta.resuelta_en = datetime.now(UTC)
        alerta = await self._alerta_repo.actualizar(alerta)

        ultima_lectura = await self._lectura_repo.obtener_mas_reciente(alerta.vehiculo_id)
        km_base = ultima_lectura.kilometraje_km if ultima_lectura else alerta.kilometraje_km
        horas_base = ultima_lectura.horas_motor if ultima_lectura else alerta.horas_motor
        await self._estado_repo.actualizar_base(
            alerta.vehiculo_id, alerta.tipo, km_base, horas_base
        )

        return alerta
