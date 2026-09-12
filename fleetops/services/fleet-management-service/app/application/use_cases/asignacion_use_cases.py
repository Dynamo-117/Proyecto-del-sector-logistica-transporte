from __future__ import annotations

from uuid import UUID

from app.application.ports.events import EventPublisher
from app.application.ports.repositories import ConductorRepository, VehiculoRepository
from app.domain.entities import EstadoConductor, EstadoVehiculo, Vehiculo
from app.domain.exceptions import (
    ConductorNoDisponible,
    ConductorNoEncontrado,
    VehiculoNoDisponible,
    VehiculoNoEncontrado,
)


class AsignarConductorAVehiculo:
    """Asigna un conductor a un vehiculo.

    Usa lecturas con lock de fila para que, ante dos peticiones concurrentes
    sobre el mismo vehiculo/conductor, la segunda vea el estado ya actualizado
    por la primera y falle con un error de dominio en lugar de pisar la asignacion.
    """

    def __init__(
        self,
        vehiculo_repo: VehiculoRepository,
        conductor_repo: ConductorRepository,
        publisher: EventPublisher,
    ):
        self._vehiculo_repo = vehiculo_repo
        self._conductor_repo = conductor_repo
        self._publisher = publisher

    async def ejecutar(self, vehiculo_id: UUID, conductor_id: UUID) -> Vehiculo:
        vehiculo = await self._vehiculo_repo.obtener_por_id_bloqueado(vehiculo_id)
        if vehiculo is None:
            raise VehiculoNoEncontrado(f"Vehiculo '{vehiculo_id}' no encontrado")

        conductor = await self._conductor_repo.obtener_por_id_bloqueado(conductor_id)
        if conductor is None:
            raise ConductorNoEncontrado(f"Conductor '{conductor_id}' no encontrado")

        if vehiculo.conductor_id == conductor_id:
            return vehiculo

        if vehiculo.estado != EstadoVehiculo.DISPONIBLE or vehiculo.conductor_id is not None:
            raise VehiculoNoDisponible(
                f"Vehiculo '{vehiculo_id}' no esta disponible para asignacion"
            )

        if conductor.estado != EstadoConductor.DISPONIBLE:
            raise ConductorNoDisponible(f"Conductor '{conductor_id}' no esta disponible")

        vehiculo.asignar_conductor(conductor_id)
        conductor.marcar_asignado()

        vehiculo = await self._vehiculo_repo.actualizar(vehiculo)
        await self._conductor_repo.actualizar(conductor)

        await self._publisher.publicar(
            "vehiculo.conductor_asignado",
            {"vehiculo_id": str(vehiculo_id), "conductor_id": str(conductor_id)},
        )
        return vehiculo


class DesasignarConductorDeVehiculo:
    def __init__(
        self,
        vehiculo_repo: VehiculoRepository,
        conductor_repo: ConductorRepository,
        publisher: EventPublisher,
    ):
        self._vehiculo_repo = vehiculo_repo
        self._conductor_repo = conductor_repo
        self._publisher = publisher

    async def ejecutar(self, vehiculo_id: UUID) -> Vehiculo:
        vehiculo = await self._vehiculo_repo.obtener_por_id_bloqueado(vehiculo_id)
        if vehiculo is None:
            raise VehiculoNoEncontrado(f"Vehiculo '{vehiculo_id}' no encontrado")

        conductor_id = vehiculo.conductor_id
        if conductor_id is None:
            return vehiculo

        conductor = await self._conductor_repo.obtener_por_id_bloqueado(conductor_id)

        vehiculo.desasignar_conductor()
        vehiculo = await self._vehiculo_repo.actualizar(vehiculo)

        if conductor is not None:
            conductor.marcar_disponible()
            await self._conductor_repo.actualizar(conductor)

        await self._publisher.publicar(
            "vehiculo.conductor_desasignado",
            {"vehiculo_id": str(vehiculo_id), "conductor_id": str(conductor_id)},
        )
        return vehiculo
