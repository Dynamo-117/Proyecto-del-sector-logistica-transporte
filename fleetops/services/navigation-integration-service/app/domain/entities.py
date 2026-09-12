from __future__ import annotations

from dataclasses import dataclass

from app.domain.exceptions import CoordenadaInvalida


@dataclass(frozen=True)
class Coordenada:
    latitud: float
    longitud: float

    def __post_init__(self) -> None:
        if not -90.0 <= self.latitud <= 90.0:
            raise CoordenadaInvalida(f"Latitud fuera de rango: {self.latitud}")
        if not -180.0 <= self.longitud <= 180.0:
            raise CoordenadaInvalida(f"Longitud fuera de rango: {self.longitud}")


@dataclass(frozen=True)
class Ruta:
    origen: Coordenada
    destino: Coordenada
    distancia_km: float
    duracion_min: float
    puntos: list[Coordenada]
