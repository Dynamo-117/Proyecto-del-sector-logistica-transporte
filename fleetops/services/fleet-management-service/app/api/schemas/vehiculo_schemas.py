from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import EstadoVehiculo, TipoVehiculo


class VehiculoCreate(BaseModel):
    placa: str = Field(..., min_length=3, max_length=20, examples=["ABC123"])
    tipo: TipoVehiculo
    capacidad_kg: float = Field(..., gt=0, description="Capacidad de carga en kilogramos")


class VehiculoUpdate(BaseModel):
    tipo: TipoVehiculo | None = None
    capacidad_kg: float | None = Field(default=None, gt=0)
    estado: EstadoVehiculo | None = None


class VehiculoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    placa: str
    tipo: TipoVehiculo
    capacidad_kg: float
    estado: EstadoVehiculo
    conductor_id: UUID | None
    creado_en: datetime
    actualizado_en: datetime
