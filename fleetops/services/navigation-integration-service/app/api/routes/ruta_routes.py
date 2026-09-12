from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_calcular_ruta
from app.api.schemas.ruta_schemas import CalcularRutaRequest, RutaResponse
from app.application.use_cases.ruta_use_cases import CalcularRuta
from app.domain.entities import Coordenada

router = APIRouter(prefix="/rutas", tags=["rutas"])


@router.post(
    "/calcular",
    response_model=RutaResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcular ruta entre dos puntos",
    description="Interfaz propia y normalizada sobre el proveedor externo de navegacion (OSRM).",
)
async def calcular_ruta(
    payload: CalcularRutaRequest,
    use_case: Annotated[CalcularRuta, Depends(get_calcular_ruta)],
) -> RutaResponse:
    origen = Coordenada(latitud=payload.origen.latitud, longitud=payload.origen.longitud)
    destino = Coordenada(latitud=payload.destino.latitud, longitud=payload.destino.longitud)

    ruta = await use_case.ejecutar(origen, destino)
    return RutaResponse.model_validate(ruta)
