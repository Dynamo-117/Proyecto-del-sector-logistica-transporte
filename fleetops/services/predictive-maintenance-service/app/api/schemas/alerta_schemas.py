from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.entities import Alerta, EstadoAlerta, TipoAlerta
from app.domain.tipos_mantenimiento import FABRICA_TIPOS


class TipoMantenimientoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nombre: str
    descripcion: str
    recomendacion: str
    prioridad: str
    intervalo_km: float
    intervalo_horas: float


class AlertaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vehiculo_id: UUID
    tipo: TipoAlerta
    tipo_info: TipoMantenimientoResponse
    estado: EstadoAlerta
    kilometraje_km: float
    horas_motor: float
    generada_en: datetime
    resuelta_en: datetime | None

    @classmethod
    def desde_alerta(cls, alerta: Alerta) -> "AlertaResponse":
        """El estado compartido del tipo (texto, prioridad, umbrales) sale del
        peso ligero que entrega la fabrica, no se copia en cada alerta."""
        return cls(
            id=alerta.id,
            vehiculo_id=alerta.vehiculo_id,
            tipo=alerta.tipo,
            tipo_info=TipoMantenimientoResponse.model_validate(FABRICA_TIPOS.obtener(alerta.tipo)),
            estado=alerta.estado,
            kilometraje_km=alerta.kilometraje_km,
            horas_motor=alerta.horas_motor,
            generada_en=alerta.generada_en,
            resuelta_en=alerta.resuelta_en,
        )


class IngestaConAlertasResponse(BaseModel):
    kilometraje_km: float
    horas_motor: float
    alertas_generadas: list[AlertaResponse]
