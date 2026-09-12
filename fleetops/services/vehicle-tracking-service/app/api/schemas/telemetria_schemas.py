from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import EstadoMovimiento


class TelemetriaIngesta(BaseModel):
    vehiculo_id: UUID
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)
    velocidad_kmh: float = Field(..., ge=0)
    timestamp: datetime | None = Field(
        default=None, description="Si se omite, se usa la hora actual"
    )


class TelemetriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vehiculo_id: UUID
    latitud: float
    longitud: float
    velocidad_kmh: float
    timestamp: datetime


class EstadoActualResponse(TelemetriaResponse):
    estado_movimiento: EstadoMovimiento
