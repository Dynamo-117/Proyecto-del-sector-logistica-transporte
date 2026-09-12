from __future__ import annotations

from uuid import UUID

from app.domain.entities import (
    Alerta,
    EstadoAlerta,
    EstadoMantenimiento,
    LecturaOdometro,
    TipoAlerta,
    VehiculoConocido,
)


class FakeVehiculoConocidoRepository:
    def __init__(self):
        self._vehiculos: dict[UUID, VehiculoConocido] = {}

    async def existe(self, vehiculo_id: UUID) -> bool:
        return vehiculo_id in self._vehiculos

    async def registrar_o_actualizar(self, vehiculo: VehiculoConocido) -> VehiculoConocido:
        self._vehiculos[vehiculo.id] = vehiculo
        return vehiculo


class FakeLecturaOdometroRepository:
    def __init__(self):
        self._lecturas: list[LecturaOdometro] = []

    async def guardar(self, lectura: LecturaOdometro) -> LecturaOdometro:
        self._lecturas.append(lectura)
        return lectura

    async def obtener_mas_reciente(self, vehiculo_id: UUID) -> LecturaOdometro | None:
        lecturas = [lectura for lectura in self._lecturas if lectura.vehiculo_id == vehiculo_id]
        if not lecturas:
            return None
        return max(lecturas, key=lambda lectura: lectura.timestamp)


class FakeEstadoMantenimientoRepository:
    def __init__(self):
        self._estados: dict[tuple[UUID, TipoAlerta], EstadoMantenimiento] = {}

    async def obtener_todos(self, vehiculo_id: UUID) -> dict[TipoAlerta, EstadoMantenimiento]:
        return {
            tipo: estado for (v_id, tipo), estado in self._estados.items() if v_id == vehiculo_id
        }

    async def actualizar_base(
        self, vehiculo_id: UUID, tipo: TipoAlerta, km_base: float, horas_base: float
    ) -> None:
        self._estados[(vehiculo_id, tipo)] = EstadoMantenimiento(
            vehiculo_id=vehiculo_id, tipo=tipo, km_base=km_base, horas_base=horas_base
        )


class FakeAlertaRepository:
    def __init__(self):
        self._alertas: dict[UUID, Alerta] = {}

    async def crear(self, alerta: Alerta) -> Alerta:
        self._alertas[alerta.id] = alerta
        return alerta

    async def obtener(self, alerta_id: UUID) -> Alerta | None:
        return self._alertas.get(alerta_id)

    async def existe_activa(self, vehiculo_id: UUID, tipo: TipoAlerta) -> bool:
        return any(
            a.vehiculo_id == vehiculo_id and a.tipo == tipo and a.estado == EstadoAlerta.ACTIVA
            for a in self._alertas.values()
        )

    async def listar_por_vehiculo(self, vehiculo_id: UUID, estado: EstadoAlerta) -> list[Alerta]:
        return [
            a for a in self._alertas.values() if a.vehiculo_id == vehiculo_id and a.estado == estado
        ]

    async def actualizar(self, alerta: Alerta) -> Alerta:
        self._alertas[alerta.id] = alerta
        return alerta
