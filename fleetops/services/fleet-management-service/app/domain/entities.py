from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4


class TipoVehiculo(str, Enum):
    CAMION = "CAMION"
    FURGON = "FURGON"
    MOTO = "MOTO"
    VAN = "VAN"


class EstadoVehiculo(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    EN_RUTA = "EN_RUTA"
    MANTENIMIENTO = "MANTENIMIENTO"
    INACTIVO = "INACTIVO"


class EstadoConductor(str, Enum):
    DISPONIBLE = "DISPONIBLE"
    ASIGNADO = "ASIGNADO"
    INACTIVO = "INACTIVO"


class RolUsuario(str, Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    OPERADOR = "OPERADOR"


@dataclass
class Vehiculo:
    placa: str
    tipo: TipoVehiculo
    capacidad_kg: float
    id: UUID = field(default_factory=uuid4)
    estado: EstadoVehiculo = EstadoVehiculo.DISPONIBLE
    conductor_id: UUID | None = None
    creado_en: datetime = field(default_factory=lambda: datetime.now(UTC))
    actualizado_en: datetime = field(default_factory=lambda: datetime.now(UTC))

    def asignar_conductor(self, conductor_id: UUID) -> None:
        self.conductor_id = conductor_id
        self.estado = EstadoVehiculo.EN_RUTA
        self.actualizado_en = datetime.now(UTC)

    def desasignar_conductor(self) -> None:
        self.conductor_id = None
        self.estado = EstadoVehiculo.DISPONIBLE
        self.actualizado_en = datetime.now(UTC)


@dataclass
class Conductor:
    nombre: str
    licencia: str
    id: UUID = field(default_factory=uuid4)
    estado: EstadoConductor = EstadoConductor.DISPONIBLE
    creado_en: datetime = field(default_factory=lambda: datetime.now(UTC))
    actualizado_en: datetime = field(default_factory=lambda: datetime.now(UTC))

    def marcar_asignado(self) -> None:
        self.estado = EstadoConductor.ASIGNADO
        self.actualizado_en = datetime.now(UTC)

    def marcar_disponible(self) -> None:
        self.estado = EstadoConductor.DISPONIBLE
        self.actualizado_en = datetime.now(UTC)


@dataclass
class Usuario:
    email: str
    password_hash: str
    id: UUID = field(default_factory=uuid4)
    rol: RolUsuario = RolUsuario.OPERADOR
    activo: bool = True
    creado_en: datetime = field(default_factory=lambda: datetime.now(UTC))
    actualizado_en: datetime = field(default_factory=lambda: datetime.now(UTC))
