from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_resumen_facade
from app.api.schemas.resumen_schemas import ResumenOperativoResponse
from app.application.facade.resumen_operativo_facade import ResumenOperativoFacade

router = APIRouter(tags=["resumen"])


@router.get(
    "/resumen",
    response_model=ResumenOperativoResponse,
    summary="Resumen operativo de toda la flota",
    description=(
        "Una sola llamada que consulta flota, rutas, mantenimiento y tracking y devuelve "
        "el resumen ya armado (patron Facade). Si un servicio esta caido, su seccion "
        "llega con disponible=false en vez de fallar todo el resumen."
    ),
)
async def resumen_operativo(
    request: Request,
    facade: Annotated[ResumenOperativoFacade, Depends(get_resumen_facade)],
) -> ResumenOperativoResponse:
    headers = {}
    autorizacion = request.headers.get("authorization")
    if autorizacion:
        headers["authorization"] = autorizacion
    resumen = await facade.obtener(headers)
    return ResumenOperativoResponse.model_validate(resumen)
