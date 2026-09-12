from __future__ import annotations

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


class FakeNodoRepository:
    def __init__(self):
        self._nodos: dict[UUID, Nodo] = {}

    async def crear(self, nodo: Nodo) -> Nodo:
        self._nodos[nodo.id] = nodo
        return nodo

    async def obtener(self, nodo_id: UUID) -> Nodo | None:
        return self._nodos.get(nodo_id)

    async def listar(self) -> list[Nodo]:
        return list(self._nodos.values())


class FakeAristaRepository:
    def __init__(self):
        self._aristas: list[Arista] = []

    async def crear(self, arista: Arista) -> Arista:
        self._aristas.append(arista)
        return arista

    async def listar_todas(self) -> list[Arista]:
        return list(self._aristas)


class FakeCargaRepository:
    def __init__(self):
        self._cargas: dict[UUID, Carga] = {}

    async def crear(self, carga: Carga) -> Carga:
        self._cargas[carga.id] = carga
        return carga

    async def actualizar_estado(self, carga_id: UUID, estado: EstadoCarga) -> Carga:
        carga = self._cargas[carga_id]
        carga.estado = estado
        return carga

    async def obtener(self, carga_id: UUID) -> Carga | None:
        return self._cargas.get(carga_id)


class FakeRutaRepository:
    def __init__(self):
        self._rutas: dict[UUID, Ruta] = {}

    async def crear(self, ruta: Ruta) -> Ruta:
        self._rutas[ruta.id] = ruta
        return ruta

    async def obtener(self, ruta_id: UUID) -> Ruta | None:
        return self._rutas.get(ruta_id)

    async def listar_por_estado(self, estado: EstadoRuta) -> list[Ruta]:
        return [r for r in self._rutas.values() if r.estado == estado]

    async def existe_ruta_activa_para_vehiculo(self, vehiculo_id: UUID) -> bool:
        return any(
            r.vehiculo_id == vehiculo_id and r.estado == EstadoRuta.ACTIVA
            for r in self._rutas.values()
        )


class FakeVehiculoDisponibleRepository:
    def __init__(self):
        self._vehiculos: dict[UUID, VehiculoDisponible] = {}

    async def registrar_o_actualizar(self, vehiculo: VehiculoDisponible) -> VehiculoDisponible:
        self._vehiculos[vehiculo.id] = vehiculo
        return vehiculo

    async def actualizar_estado(self, vehiculo_id: UUID, estado: EstadoVehiculo) -> None:
        if vehiculo_id in self._vehiculos:
            self._vehiculos[vehiculo_id].estado = estado

    async def obtener(self, vehiculo_id: UUID) -> VehiculoDisponible | None:
        return self._vehiculos.get(vehiculo_id)

    async def listar_candidatos_bloqueado(self, peso_kg: float) -> list[VehiculoDisponible]:
        candidatos = [
            v
            for v in self._vehiculos.values()
            if v.estado == EstadoVehiculo.DISPONIBLE and v.capacidad_kg >= peso_kg
        ]
        return sorted(candidatos, key=lambda v: v.capacidad_kg)
