from __future__ import annotations

from uuid import UUID

from app.application.ports.repositories import AristaRepository, NodoRepository
from app.domain.entities import Arista, Nodo
from app.domain.exceptions import NodoNoEncontrado


class CrearNodo:
    def __init__(self, repo: NodoRepository):
        self._repo = repo

    async def ejecutar(self, nombre: str, latitud: float, longitud: float) -> Nodo:
        return await self._repo.crear(Nodo(nombre=nombre, latitud=latitud, longitud=longitud))


class ListarNodos:
    def __init__(self, repo: NodoRepository):
        self._repo = repo

    async def ejecutar(self) -> list[Nodo]:
        return await self._repo.listar()


class CrearConexion:
    def __init__(self, nodo_repo: NodoRepository, arista_repo: AristaRepository):
        self._nodo_repo = nodo_repo
        self._arista_repo = arista_repo

    async def ejecutar(
        self, nodo_origen_id: UUID, nodo_destino_id: UUID, distancia_km: float
    ) -> Arista:
        if await self._nodo_repo.obtener(nodo_origen_id) is None:
            raise NodoNoEncontrado(f"Nodo '{nodo_origen_id}' no encontrado")
        if await self._nodo_repo.obtener(nodo_destino_id) is None:
            raise NodoNoEncontrado(f"Nodo '{nodo_destino_id}' no encontrado")

        arista = Arista(
            nodo_origen_id=nodo_origen_id,
            nodo_destino_id=nodo_destino_id,
            distancia_km=distancia_km,
        )
        return await self._arista_repo.crear(arista)
