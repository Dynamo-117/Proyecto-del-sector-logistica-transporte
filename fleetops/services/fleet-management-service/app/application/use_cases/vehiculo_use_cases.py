from __future__ import annotations

from uuid import UUID

from app.application.ports.events import EventPublisher
from app.application.ports.repositories import VehiculoRepository
from app.domain.entities import EstadoVehiculo, TipoVehiculo, Vehiculo
from app.domain.exceptions import PlacaDuplicada, VehiculoNoEncontrado


class CrearVehiculo:
    def __init__(self, repo: VehiculoRepository, publisher: EventPublisher):
        self._repo = repo
        self._publisher = publisher

    async def ejecutar(self, placa: str, tipo: TipoVehiculo, capacidad_kg: float) -> Vehiculo:
        existente = await self._repo.obtener_por_placa(placa)
        if existente is not None:
            raise PlacaDuplicada(f"Ya existe un vehiculo con placa '{placa}'")

        vehiculo = Vehiculo(placa=placa, tipo=tipo, capacidad_kg=capacidad_kg)
        vehiculo = await self._repo.crear(vehiculo)

        await self._publisher.publicar(
            "vehiculo.creado",
            {
                "id": str(vehiculo.id),
                "placa": vehiculo.placa,
                "tipo": vehiculo.tipo.value,
                "capacidad_kg": vehiculo.capacidad_kg,
                "estado": vehiculo.estado.value,
            },
        )
        return vehiculo


class ObtenerVehiculo:
    def __init__(self, repo: VehiculoRepository):
        self._repo = repo

    async def ejecutar(self, vehiculo_id: UUID) -> Vehiculo:
        vehiculo = await self._repo.obtener_por_id(vehiculo_id)
        if vehiculo is None:
            raise VehiculoNoEncontrado(f"Vehiculo '{vehiculo_id}' no encontrado")
        return vehiculo


class ListarVehiculos:
    def __init__(self, repo: VehiculoRepository):
        self._repo = repo

    async def ejecutar(self, skip: int = 0, limit: int = 100) -> list[Vehiculo]:
        return await self._repo.listar(skip=skip, limit=limit)


class ActualizarVehiculo:
    def __init__(self, repo: VehiculoRepository, publisher: EventPublisher):
        self._repo = repo
        self._publisher = publisher

    async def ejecutar(
        self,
        vehiculo_id: UUID,
        tipo: TipoVehiculo | None = None,
        capacidad_kg: float | None = None,
        estado: EstadoVehiculo | None = None,
    ) -> Vehiculo:
        vehiculo = await self._repo.obtener_por_id(vehiculo_id)
        if vehiculo is None:
            raise VehiculoNoEncontrado(f"Vehiculo '{vehiculo_id}' no encontrado")

        if tipo is not None:
            vehiculo.tipo = tipo
        if capacidad_kg is not None:
            vehiculo.capacidad_kg = capacidad_kg
        if estado is not None:
            vehiculo.estado = estado

        vehiculo = await self._repo.actualizar(vehiculo)

        await self._publisher.publicar(
            "vehiculo.actualizado",
            {
                "id": str(vehiculo.id),
                "placa": vehiculo.placa,
                "tipo": vehiculo.tipo.value,
                "capacidad_kg": vehiculo.capacidad_kg,
                "estado": vehiculo.estado.value,
            },
        )
        return vehiculo


class EliminarVehiculo:
    def __init__(self, repo: VehiculoRepository):
        self._repo = repo

    async def ejecutar(self, vehiculo_id: UUID) -> None:
        vehiculo = await self._repo.obtener_por_id(vehiculo_id)
        if vehiculo is None:
            raise VehiculoNoEncontrado(f"Vehiculo '{vehiculo_id}' no encontrado")
        await self._repo.eliminar(vehiculo_id)
