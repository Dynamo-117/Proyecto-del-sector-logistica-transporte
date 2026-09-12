from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from app.domain.exceptions import AristaInvalida


class EstadoCarga(str, Enum):
    PENDIENTE = "PENDIENTE"
    ASIGNADA = "ASIGNADA"


class EstadoRuta(str, Enum):
    ACTIVA = "ACTIVA"
    COMPLETADA = "COMPLETADA"


class EstadoVehiculo(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    EN_RUTA = "EN_RUTA"
    MANTENIMIENTO = "MANTENIMIENTO"
    INACTIVO = "INACTIVO"


@dataclass
class Nodo:
    nombre: str
    latitud: float
    longitud: float
    id: UUID = field(default_factory=uuid4)


@dataclass
class Arista:
    nodo_origen_id: UUID
    nodo_destino_id: UUID
    distancia_km: float
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.distancia_km <= 0:
            raise AristaInvalida("La distancia entre nodos debe ser positiva")
        if self.nodo_origen_id == self.nodo_destino_id:
            raise AristaInvalida("Un nodo no puede conectarse consigo mismo")


@dataclass
class Carga:
    origen_nodo_id: UUID
    destino_nodo_id: UUID
    peso_kg: float
    volumen_m3: float
    id: UUID = field(default_factory=uuid4)
    estado: EstadoCarga = EstadoCarga.PENDIENTE
    creado_en: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Ruta:
    carga_id: UUID
    vehiculo_id: UUID
    nodos: list[UUID]
    distancia_km: float
    id: UUID = field(default_factory=uuid4)
    estado: EstadoRuta = EstadoRuta.ACTIVA
    creado_en: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class VehiculoDisponible:
    id: UUID
    placa: str
    capacidad_kg: float
    estado: EstadoVehiculo
