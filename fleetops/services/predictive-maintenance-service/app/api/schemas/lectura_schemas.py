from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LecturaOdometroCreate(BaseModel):
    vehiculo_id: UUID
    kilometraje_km: float = Field(..., ge=0)
    horas_motor: float = Field(..., ge=0)


class LecturaOdometroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vehiculo_id: UUID
    kilometraje_km: float
    horas_motor: float
    timestamp: datetime
