from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NodoCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=120)
    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)


class NodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str
    latitud: float
    longitud: float


class ConexionCreate(BaseModel):
    nodo_destino_id: UUID
    distancia_km: float = Field(..., gt=0)


class ConexionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nodo_origen_id: UUID
    nodo_destino_id: UUID
    distancia_km: float
