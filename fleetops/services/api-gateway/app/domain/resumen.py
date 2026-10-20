from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class ResumenFlota:
    disponible: bool = False
    total_vehiculos: int = 0
    vehiculos_por_estado: dict[str, int] = field(default_factory=dict)
    total_conductores: int = 0
    conductores_disponibles: int = 0


@dataclass
class ResumenRutas:
    disponible: bool = False
    rutas_activas: int = 0
    distancia_total_km: float = 0.0


@dataclass
class ResumenMantenimiento:
    disponible: bool = False
    alertas_activas: int = 0
    vehiculos_con_alertas: int = 0


@dataclass
class ResumenTracking:
    disponible: bool = False
    en_movimiento: int = 0
    detenidos: int = 0
    sin_telemetria: int = 0


@dataclass
class ResumenOperativo:
    flota: ResumenFlota
    rutas: ResumenRutas
    mantenimiento: ResumenMantenimiento
    tracking: ResumenTracking
    llamadas_internas: int = 0
    generado_en: datetime = field(default_factory=lambda: datetime.now(UTC))
