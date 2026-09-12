from pydantic import BaseModel, ConfigDict, Field


class CoordenadaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latitud: float = Field(..., ge=-90, le=90)
    longitud: float = Field(..., ge=-180, le=180)


class CalcularRutaRequest(BaseModel):
    origen: CoordenadaSchema
    destino: CoordenadaSchema


class RutaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    origen: CoordenadaSchema
    destino: CoordenadaSchema
    distancia_km: float
    duracion_min: float
    puntos: list[CoordenadaSchema]
