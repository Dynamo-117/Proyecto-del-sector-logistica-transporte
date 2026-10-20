from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from app.domain.entities import Arista


class ComponenteRuta(ABC):
    # =================   PATRON GOF: COMPOSITE (Componente) -- inicia aqui =================
    """El Componente: la interfaz comun que comparten los elementos simples (un
    Tramo) y los compuestos (un Trayecto). El cliente pide distancia, cantidad
    de tramos o recorrido sin preguntar si esta hablando con una pieza suelta o
    con todo un arbol de rutas.
    """

    nombre: str

    @abstractmethod
    def distancia_km(self) -> float: ...

    @abstractmethod
    def nodos(self) -> list[UUID]: ...

    @abstractmethod
    def cantidad_tramos(self) -> int: ...

    @abstractmethod
    def describir(self, nombres: Mapping[UUID, str]) -> dict[str, Any]: ...

    # ================= PATRON GOF: COMPOSITE (Componente) -- termina aqui =================


class Tramo(ComponenteRuta):
    # =================   PATRON GOF: COMPOSITE (Hoja) -- inicia aqui =================
    """La Hoja: un tramo simple entre dos nodos conectados directamente (una
    arista del grafo). No tiene hijos; hace el trabajo real."""

    def __init__(self, origen_id: UUID, destino_id: UUID, distancia_km: float):
        self.nombre = "tramo"
        self._origen_id = origen_id
        self._destino_id = destino_id
        self._distancia_km = distancia_km

    def distancia_km(self) -> float:
        return self._distancia_km

    def nodos(self) -> list[UUID]:
        return [self._origen_id, self._destino_id]

    def cantidad_tramos(self) -> int:
        return 1

    def describir(self, nombres: Mapping[UUID, str]) -> dict[str, Any]:
        origen = nombres.get(self._origen_id, str(self._origen_id))
        destino = nombres.get(self._destino_id, str(self._destino_id))
        return {
            "tipo": "tramo",
            "nombre": f"{origen} -> {destino}",
            "distancia_km": self._distancia_km,
            "cantidad_tramos": 1,
            "hijos": [],
        }

    # ================= PATRON GOF: COMPOSITE (Hoja) -- termina aqui =================


class Trayecto(ComponenteRuta):
    # =================   PATRON GOF: COMPOSITE (Compuesto) -- inicia aqui =================
    """El Compuesto: guarda hijos (tramos u otros trayectos) y resuelve cada
    operacion delegandola en ellos y combinando los resultados. Un itinerario
    completo es un Trayecto de Trayectos; cada trayecto es un Trayecto de Tramos.
    """

    def __init__(self, nombre: str):
        self.nombre = nombre
        self._hijos: list[ComponenteRuta] = []

    @property
    def hijos(self) -> tuple[ComponenteRuta, ...]:
        return tuple(self._hijos)

    def agregar(self, componente: ComponenteRuta) -> None:
        if componente is self:
            raise ValueError("Un trayecto no puede contenerse a si mismo")
        self._hijos.append(componente)

    def quitar(self, componente: ComponenteRuta) -> None:
        self._hijos.remove(componente)

    def distancia_km(self) -> float:
        return sum(hijo.distancia_km() for hijo in self._hijos)

    def nodos(self) -> list[UUID]:
        recorrido: list[UUID] = []
        for hijo in self._hijos:
            nodos_hijo = hijo.nodos()
            if recorrido and nodos_hijo and recorrido[-1] == nodos_hijo[0]:
                nodos_hijo = nodos_hijo[1:]
            recorrido.extend(nodos_hijo)
        return recorrido

    def cantidad_tramos(self) -> int:
        return sum(hijo.cantidad_tramos() for hijo in self._hijos)

    def describir(self, nombres: Mapping[UUID, str]) -> dict[str, Any]:
        return {
            "tipo": "trayecto",
            "nombre": self.nombre,
            "distancia_km": self.distancia_km(),
            "cantidad_tramos": self.cantidad_tramos(),
            "hijos": [hijo.describir(nombres) for hijo in self._hijos],
        }

    # ================= PATRON GOF: COMPOSITE (Compuesto) -- termina aqui =================


def construir_trayecto(nombre: str, camino: list[UUID], aristas: list[Arista]) -> Trayecto:
    """Convierte un camino de nodos (resultado de Dijkstra) en un Trayecto de
    Tramos, tomando de cada par consecutivo la arista mas corta que los une."""
    distancias: dict[frozenset[UUID], float] = {}
    for arista in aristas:
        par = frozenset((arista.nodo_origen_id, arista.nodo_destino_id))
        distancias[par] = min(arista.distancia_km, distancias.get(par, float("inf")))

    trayecto = Trayecto(nombre)
    for origen_id, destino_id in zip(camino, camino[1:], strict=False):
        trayecto.agregar(
            Tramo(origen_id, destino_id, distancias[frozenset((origen_id, destino_id))])
        )
    return trayecto
