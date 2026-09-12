from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from app.domain.exceptions import TelemetriaInvalida

UMBRAL_VELOCIDAD_EN_MOVIMIENTO_KMH = 1.0


class EstadoMovimiento(str, Enum):
    EN_MOVIMIENTO = "EN_MOVIMIENTO"
    DETENIDO = "DETENIDO"


@dataclass
class VehiculoConocido:
    id: UUID
    placa: str
    registrado_en: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Telemetria:
    vehiculo_id: UUID
    latitud: float
    longitud: float
    velocidad_kmh: float
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not -90.0 <= self.latitud <= 90.0:
            raise TelemetriaInvalida(f"Latitud fuera de rango: {self.latitud}")
        if not -180.0 <= self.longitud <= 180.0:
            raise TelemetriaInvalida(f"Longitud fuera de rango: {self.longitud}")
        if self.velocidad_kmh < 0:
            raise TelemetriaInvalida(f"Velocidad no puede ser negativa: {self.velocidad_kmh}")

    @property
    def estado_movimiento(self) -> EstadoMovimiento:
        if self.velocidad_kmh >= UMBRAL_VELOCIDAD_EN_MOVIMIENTO_KMH:
            return EstadoMovimiento.EN_MOVIMIENTO
        return EstadoMovimiento.DETENIDO
