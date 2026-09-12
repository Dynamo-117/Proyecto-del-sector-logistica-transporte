from __future__ import annotations

import heapq
from collections import defaultdict
from uuid import UUID

from app.domain.entities import Arista
from app.domain.exceptions import SinRutaEnGrafo


def calcular_ruta_mas_corta(
    aristas: list[Arista], origen_id: UUID, destino_id: UUID
) -> tuple[list[UUID], float]:
    """Dijkstra sobre un grafo no dirigido: cada arista conecta ambos nodos en
    ambos sentidos con el mismo costo (distancia en km). Devuelve la secuencia
    de nodos del origen al destino y la distancia total, o lanza SinRutaEnGrafo
    si no existe camino."""
    adyacencia: dict[UUID, list[tuple[UUID, float]]] = defaultdict(list)
    for arista in aristas:
        adyacencia[arista.nodo_origen_id].append((arista.nodo_destino_id, arista.distancia_km))
        adyacencia[arista.nodo_destino_id].append((arista.nodo_origen_id, arista.distancia_km))

    if origen_id == destino_id:
        return [origen_id], 0.0

    distancias: dict[UUID, float] = {origen_id: 0.0}
    predecesores: dict[UUID, UUID] = {}
    visitados: set[UUID] = set()
    cola: list[tuple[float, UUID]] = [(0.0, origen_id)]

    while cola:
        distancia_actual, nodo_actual = heapq.heappop(cola)
        if nodo_actual in visitados:
            continue
        visitados.add(nodo_actual)

        if nodo_actual == destino_id:
            break

        for vecino_id, costo in adyacencia.get(nodo_actual, []):
            nueva_distancia = distancia_actual + costo
            if nueva_distancia < distancias.get(vecino_id, float("inf")):
                distancias[vecino_id] = nueva_distancia
                predecesores[vecino_id] = nodo_actual
                heapq.heappush(cola, (nueva_distancia, vecino_id))

    if destino_id not in distancias:
        raise SinRutaEnGrafo(f"No existe un camino entre los nodos '{origen_id}' y '{destino_id}'")

    camino = [destino_id]
    while camino[-1] != origen_id:
        camino.append(predecesores[camino[-1]])
    camino.reverse()

    return camino, distancias[destino_id]
