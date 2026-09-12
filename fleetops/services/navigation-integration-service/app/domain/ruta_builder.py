from __future__ import annotations

from app.domain.entities import Coordenada, Ruta


class RutaBuilder:
    # ============================================================
    # PATRON GOF: BUILDER -- inicia aqui
    # ------------------------------------------------------------

    def __init__(self) -> None:
        self._origen: Coordenada | None = None
        self._destino: Coordenada | None = None
        self._distancia_km: float | None = None
        self._duracion_min: float | None = None
        self._puntos: list[Coordenada] = []

    def con_extremos(self, origen: Coordenada, destino: Coordenada) -> RutaBuilder:
        self._origen = origen
        self._destino = destino
        return self

    def con_metricas(self, *, distancia_metros: float, duracion_segundos: float) -> RutaBuilder:
        self._distancia_km = distancia_metros / 1000
        self._duracion_min = duracion_segundos / 60
        return self

    def con_geometria(self, coordenadas_lon_lat: list[tuple[float, float]]) -> RutaBuilder:
        self._puntos = [
            Coordenada(latitud=lat, longitud=lon) for lon, lat in coordenadas_lon_lat
        ]
        return self

    def construir(self) -> Ruta:
        if self._origen is None or self._destino is None:
            raise ValueError(
                "RutaBuilder: faltan los extremos -- llama a con_extremos() antes de construir()"
            )
        if self._distancia_km is None or self._duracion_min is None:
            raise ValueError(
                "RutaBuilder: faltan las metricas -- llama a con_metricas() antes de construir()"
            )
        return Ruta(
            origen=self._origen,
            destino=self._destino,
            distancia_km=self._distancia_km,
            duracion_min=self._duracion_min,
            puntos=self._puntos,
        )

    # ================= PATRON GOF: BUILDER -- termina aqui =================
