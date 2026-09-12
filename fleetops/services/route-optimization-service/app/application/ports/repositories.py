from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.entities import (
    Arista,
    Carga,
    EstadoCarga,
    EstadoRuta,
    EstadoVehiculo,
    Nodo,
    Ruta,
    VehiculoDisponible,
)


class NodoRepository(Protocol):
    async def crear(self, nodo: Nodo) -> Nodo: ...

    async def obtener(self, nodo_id: UUID) -> Nodo | None: ...

    async def listar(self) -> list[Nodo]: ...


class AristaRepository(Protocol):
    async def crear(self, arista: Arista) -> Arista: ...

    async def listar_todas(self) -> list[Arista]: ...


class CargaRepository(Protocol):
    async def crear(self, carga: Carga) -> Carga: ...

    async def actualizar_estado(self, carga_id: UUID, estado: EstadoCarga) -> Carga: ...

    async def obtener(self, carga_id: UUID) -> Carga | None: ...


class RutaRepository(Protocol):
    async def crear(self, ruta: Ruta) -> Ruta: ...

    async def obtener(self, ruta_id: UUID) -> Ruta | None: ...

    async def listar_por_estado(self, estado: EstadoRuta) -> list[Ruta]: ...

    async def existe_ruta_activa_para_vehiculo(self, vehiculo_id: UUID) -> bool: ...


class VehiculoDisponibleRepository(Protocol):
    async def registrar_o_actualizar(self, vehiculo: VehiculoDisponible) -> VehiculoDisponible: ...

    async def actualizar_estado(self, vehiculo_id: UUID, estado: EstadoVehiculo) -> None: ...

    async def obtener(self, vehiculo_id: UUID) -> VehiculoDisponible | None: ...

    async def listar_candidatos_bloqueado(self, peso_kg: float) -> list[VehiculoDisponible]:
        """Vehiculos con estado DISPONIBLE y capacidad suficiente, ordenados por
        capacidad ascendente (best-fit), bloqueando sus filas (SELECT FOR UPDATE)
        para evitar que dos solicitudes concurrentes elijan el mismo vehiculo."""
        ...
