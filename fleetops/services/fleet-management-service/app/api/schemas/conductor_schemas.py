from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import EstadoConductor


class ConductorCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    licencia: str = Field(..., min_length=3, max_length=30)


class ConductorUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    estado: EstadoConductor | None = None


class ConductorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str
    licencia: str
    estado: EstadoConductor
    creado_en: datetime
    actualizado_en: datetime
