from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.entities import EstadoAlerta, TipoAlerta


class AlertaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vehiculo_id: UUID
    tipo: TipoAlerta
    estado: EstadoAlerta
    kilometraje_km: float
    horas_motor: float
    generada_en: datetime
    resuelta_en: datetime | None


class IngestaConAlertasResponse(BaseModel):
    kilometraje_km: float
    horas_motor: float
    alertas_generadas: list[AlertaResponse]
