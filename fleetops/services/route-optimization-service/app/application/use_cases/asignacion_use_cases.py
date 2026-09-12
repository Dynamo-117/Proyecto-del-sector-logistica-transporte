from __future__ import annotations

from uuid import UUID

from app.application.ports.repositories import (
    AristaRepository,
    CargaRepository,
    NodoRepository,
    RutaRepository,
    VehiculoDisponibleRepository,
)
from app.domain.entities import Carga, EstadoCarga, EstadoRuta, Ruta
from app.domain.exceptions import NodoNoEncontrado, RutaNoEncontrada, SinVehiculoDisponible
from app.domain.grafo import calcular_ruta_mas_corta


class SolicitarAsignacionCarga:
    """Caso de uso principal: calcula la ruta mas corta entre dos nodos del
    grafo (Dijkstra) y asigna, con un criterio greedy de mejor ajuste (menor
    capacidad suficiente), el primer vehiculo disponible libre encontrado.

    La seleccion del vehiculo bloquea las filas candidatas (SELECT FOR UPDATE)
    para que dos solicitudes concurrentes no terminen asignando el mismo
    vehiculo a dos cargas distintas.
    """

    def __init__(
        self,
        nodo_repo: NodoRepository,
        arista_repo: AristaRepository,
        carga_repo: CargaRepository,
        ruta_repo: RutaRepository,
        vehiculo_repo: VehiculoDisponibleRepository,
    ):
        self._nodo_repo = nodo_repo
        self._arista_repo = arista_repo
        self._carga_repo = carga_repo
        self._ruta_repo = ruta_repo
        self._vehiculo_repo = vehiculo_repo

    async def ejecutar(
        self, origen_nodo_id: UUID, destino_nodo_id: UUID, peso_kg: float, volumen_m3: float
    ) -> Ruta:
        if await self._nodo_repo.obtener(origen_nodo_id) is None:
            raise NodoNoEncontrado(f"Nodo '{origen_nodo_id}' no encontrado")
        if await self._nodo_repo.obtener(destino_nodo_id) is None:
            raise NodoNoEncontrado(f"Nodo '{destino_nodo_id}' no encontrado")

        aristas = await self._arista_repo.listar_todas()
        nodos_camino, distancia_km = calcular_ruta_mas_corta(
            aristas, origen_nodo_id, destino_nodo_id
        )

        carga = await self._carga_repo.crear(
            Carga(
                origen_nodo_id=origen_nodo_id,
                destino_nodo_id=destino_nodo_id,
                peso_kg=peso_kg,
                volumen_m3=volumen_m3,
            )
        )

        vehiculo_elegido = None
        for candidato in await self._vehiculo_repo.listar_candidatos_bloqueado(peso_kg):
            if not await self._ruta_repo.existe_ruta_activa_para_vehiculo(candidato.id):
                vehiculo_elegido = candidato
                break

        if vehiculo_elegido is None:
            raise SinVehiculoDisponible(
                f"No hay vehiculos disponibles con capacidad para {peso_kg} kg"
            )

        ruta = await self._ruta_repo.crear(
            Ruta(
                carga_id=carga.id,
                vehiculo_id=vehiculo_elegido.id,
                nodos=nodos_camino,
                distancia_km=distancia_km,
            )
        )
        await self._carga_repo.actualizar_estado(carga.id, EstadoCarga.ASIGNADA)

        return ruta


class ObtenerRuta:
    def __init__(self, repo: RutaRepository):
        self._repo = repo

    async def ejecutar(self, ruta_id: UUID) -> Ruta:
        ruta = await self._repo.obtener(ruta_id)
        if ruta is None:
            raise RutaNoEncontrada(f"Ruta '{ruta_id}' no encontrada")
        return ruta


class ListarRutasActivas:
    def __init__(self, repo: RutaRepository):
        self._repo = repo

    async def ejecutar(self) -> list[Ruta]:
        return await self._repo.listar_por_estado(EstadoRuta.ACTIVA)
