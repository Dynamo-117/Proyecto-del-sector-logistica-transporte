from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from app.domain.exceptions import LecturaInvalida


class TipoAlerta(str, Enum):
    CAMBIO_ACEITE = "CAMBIO_ACEITE"
    REVISION_GENERAL = "REVISION_GENERAL"


class EstadoAlerta(str, Enum):
    ACTIVA = "ACTIVA"
    RESUELTA = "RESUELTA"


@dataclass(frozen=True)
class UmbralMantenimiento:
    intervalo_km: float
    intervalo_horas: float


UMBRALES_MANTENIMIENTO: dict[TipoAlerta, UmbralMantenimiento] = {
    TipoAlerta.CAMBIO_ACEITE: UmbralMantenimiento(intervalo_km=10_000, intervalo_horas=300),
    TipoAlerta.REVISION_GENERAL: UmbralMantenimiento(intervalo_km=20_000, intervalo_horas=600),
}


@dataclass
class VehiculoConocido:
    id: UUID
    placa: str


@dataclass
class LecturaOdometro:
    vehiculo_id: UUID
    kilometraje_km: float
    horas_motor: float
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.kilometraje_km < 0:
            raise LecturaInvalida("El kilometraje no puede ser negativo")
        if self.horas_motor < 0:
            raise LecturaInvalida("Las horas de motor no pueden ser negativas")


@dataclass
class Alerta:
    vehiculo_id: UUID
    tipo: TipoAlerta
    kilometraje_km: float
    horas_motor: float
    id: UUID = field(default_factory=uuid4)
    estado: EstadoAlerta = EstadoAlerta.ACTIVA
    generada_en: datetime = field(default_factory=lambda: datetime.now(UTC))
    resuelta_en: datetime | None = None


@dataclass
class EstadoMantenimiento:
    """Marca de referencia (km/horas) desde la que se cuenta el desgaste para
    un tipo de mantenimiento dado, actualizada cada vez que se completa uno."""

    vehiculo_id: UUID
    tipo: TipoAlerta
    km_base: float = 0.0
    horas_base: float = 0.0


def evaluar_tipos_a_alertar(
    kilometraje_actual: float,
    horas_actual: float,
    estados_actuales: dict[TipoAlerta, EstadoMantenimiento],
) -> list[TipoAlerta]:
    """Compara el desgaste acumulado desde el ultimo mantenimiento de cada tipo
    contra su umbral fijo, y devuelve los tipos que deberian generar alerta."""
    tipos_a_alertar = []
    for tipo, umbral in UMBRALES_MANTENIMIENTO.items():
        estado = estados_actuales.get(tipo)
        km_base = estado.km_base if estado else 0.0
        horas_base = estado.horas_base if estado else 0.0

        km_recorridos = kilometraje_actual - km_base
        horas_transcurridas = horas_actual - horas_base

        if km_recorridos >= umbral.intervalo_km or horas_transcurridas >= umbral.intervalo_horas:
            tipos_a_alertar.append(tipo)

    return tipos_a_alertar
