from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.entities import (
    Alerta,
    EstadoAlerta,
    EstadoMantenimiento,
    LecturaOdometro,
    TipoAlerta,
    VehiculoConocido,
)


class VehiculoConocidoRepository(Protocol):
    async def existe(self, vehiculo_id: UUID) -> bool: ...

    async def registrar_o_actualizar(self, vehiculo: VehiculoConocido) -> VehiculoConocido: ...


class LecturaOdometroRepository(Protocol):
    async def guardar(self, lectura: LecturaOdometro) -> LecturaOdometro: ...

    async def obtener_mas_reciente(self, vehiculo_id: UUID) -> LecturaOdometro | None: ...


class EstadoMantenimientoRepository(Protocol):
    async def obtener_todos(self, vehiculo_id: UUID) -> dict[TipoAlerta, EstadoMantenimiento]: ...

    async def actualizar_base(
        self, vehiculo_id: UUID, tipo: TipoAlerta, km_base: float, horas_base: float
    ) -> None: ...


class AlertaRepository(Protocol):
    async def crear(self, alerta: Alerta) -> Alerta: ...

    async def obtener(self, alerta_id: UUID) -> Alerta | None: ...

    async def existe_activa(self, vehiculo_id: UUID, tipo: TipoAlerta) -> bool: ...

    async def listar_por_vehiculo(
        self, vehiculo_id: UUID, estado: EstadoAlerta
    ) -> list[Alerta]: ...

    async def actualizar(self, alerta: Alerta) -> Alerta: ...
