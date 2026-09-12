from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import EstadoRuta


class SolicitudCargaCreate(BaseModel):
    origen_nodo_id: UUID
    destino_nodo_id: UUID
    peso_kg: float = Field(..., gt=0)
    volumen_m3: float = Field(..., gt=0)


class RutaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    carga_id: UUID
    vehiculo_id: UUID
    vehiculo_placa: str | None = None
    nodos: list[UUID]
    distancia_km: float
    estado: EstadoRuta
    creado_en: datetime
