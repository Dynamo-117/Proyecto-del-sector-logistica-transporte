from __future__ import annotations

from uuid import UUID

from app.application.ports.repositories import VehiculoDisponibleRepository
from app.core.logging import get_logger
from app.domain.entities import EstadoVehiculo, VehiculoDisponible

logger = get_logger(__name__)


class SincronizarVehiculoDisponible:
    """Mantiene al dia el modelo de lectura local de vehiculos a partir de los
    eventos publicados por fleet-management-service ('vehiculo.creado' y
    'vehiculo.actualizado' traen el estado completo del vehiculo)."""

    def __init__(self, repo: VehiculoDisponibleRepository):
        self._repo = repo

    async def ejecutar(
        self, vehiculo_id: UUID, placa: str, capacidad_kg: float, estado: str
    ) -> VehiculoDisponible:
        vehiculo = VehiculoDisponible(
            id=vehiculo_id, placa=placa, capacidad_kg=capacidad_kg, estado=EstadoVehiculo(estado)
        )
        return await self._repo.registrar_o_actualizar(vehiculo)


class ActualizarEstadoVehiculoPorAsignacionConductor:
    """Ante 'vehiculo.conductor_asignado'/'vehiculo.conductor_desasignado' (que no
    traen el estado completo del vehiculo), se refleja localmente el cambio de
    disponibilidad que ese evento implica en fleet-management-service."""

    def __init__(self, repo: VehiculoDisponibleRepository):
        self._repo = repo

    async def ejecutar(self, vehiculo_id: UUID, estado: EstadoVehiculo) -> None:
        vehiculo = await self._repo.obtener(vehiculo_id)
        if vehiculo is None:
            logger.warning(
                "vehiculo_desconocido_al_sincronizar_estado", vehiculo_id=str(vehiculo_id)
            )
            return
        await self._repo.actualizar_estado(vehiculo_id, estado)
