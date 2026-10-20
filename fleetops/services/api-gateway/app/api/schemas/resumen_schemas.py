from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumenFlotaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    disponible: bool
    total_vehiculos: int
    vehiculos_por_estado: dict[str, int]
    total_conductores: int
    conductores_disponibles: int


class ResumenRutasResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    disponible: bool
    rutas_activas: int
    distancia_total_km: float


class ResumenMantenimientoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    disponible: bool
    alertas_activas: int
    vehiculos_con_alertas: int


class ResumenTrackingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    disponible: bool
    en_movimiento: int
    detenidos: int
    sin_telemetria: int


class ResumenOperativoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    flota: ResumenFlotaResponse
    rutas: ResumenRutasResponse
    mantenimiento: ResumenMantenimientoResponse
    tracking: ResumenTrackingResponse
    llamadas_internas: int
    generado_en: datetime
