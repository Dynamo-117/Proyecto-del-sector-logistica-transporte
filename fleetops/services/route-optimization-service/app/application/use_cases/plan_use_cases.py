from __future__ import annotations

from uuid import UUID

from app.application.ports.repositories import AristaRepository, NodoRepository
from app.domain.exceptions import NodoNoEncontrado, PlanInvalido
from app.domain.grafo import calcular_ruta_mas_corta
from app.domain.itinerario import Trayecto, construir_trayecto


class PlanificarRutaConParadas:
    """Arma un itinerario con varias paradas como un arbol Composite:
    Itinerario (Trayecto) -> un Trayecto por cada par de paradas consecutivas
    -> un Tramo por cada arista del camino mas corto (Dijkstra) entre ellas."""

    def __init__(self, nodo_repo: NodoRepository, arista_repo: AristaRepository):
        self._nodo_repo = nodo_repo
        self._arista_repo = arista_repo

    async def ejecutar(self, paradas: list[UUID]) -> tuple[Trayecto, dict[UUID, str]]:
        if len(paradas) < 2:
            raise PlanInvalido("Un plan necesita al menos dos paradas")

        nombres = {nodo.id: nodo.nombre for nodo in await self._nodo_repo.listar()}
        for parada_id in paradas:
            if parada_id not in nombres:
                raise NodoNoEncontrado(f"Nodo '{parada_id}' no encontrado")

        aristas = await self._arista_repo.listar_todas()
        itinerario = Trayecto("Itinerario")

        for origen_id, destino_id in zip(paradas, paradas[1:], strict=False):
            if origen_id == destino_id:
                raise PlanInvalido("Dos paradas consecutivas no pueden ser el mismo nodo")
            camino, _ = calcular_ruta_mas_corta(aristas, origen_id, destino_id)
            itinerario.agregar(
                construir_trayecto(
                    f"{nombres[origen_id]} -> {nombres[destino_id]}", camino, aristas
                )
            )

        return itinerario, nombres
