from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    VehiculoRepo,
    get_listar_rutas_activas,
    get_obtener_ruta,
    get_solicitar_asignacion,
)
from app.api.schemas.asignacion_schemas import RutaResponse, SolicitudCargaCreate
from app.application.use_cases.asignacion_use_cases import (
    ListarRutasActivas,
    ObtenerRuta,
    SolicitarAsignacionCarga,
)
from app.domain.entities import Ruta

router = APIRouter(tags=["asignacion"])


async def _a_respuesta(ruta: Ruta, vehiculo_repo: VehiculoRepo) -> RutaResponse:
    vehiculo = await vehiculo_repo.obtener(ruta.vehiculo_id)
    respuesta = RutaResponse.model_validate(ruta)
    respuesta.vehiculo_placa = vehiculo.placa if vehiculo else None
    return respuesta


@router.post(
    "/cargas",
    response_model=RutaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar asignacion de una carga",
    description=(
        "Calcula la ruta mas corta (Dijkstra) entre el nodo origen y destino, y "
        "asigna la carga al vehiculo disponible con menor capacidad suficiente."
    ),
)
async def solicitar_asignacion(
    payload: SolicitudCargaCreate,
    use_case: Annotated[SolicitarAsignacionCarga, Depends(get_solicitar_asignacion)],
    vehiculo_repo: VehiculoRepo,
) -> RutaResponse:
    ruta = await use_case.ejecutar(
        payload.origen_nodo_id, payload.destino_nodo_id, payload.peso_kg, payload.volumen_m3
    )
    return await _a_respuesta(ruta, vehiculo_repo)


@router.get(
    "/rutas",
    response_model=list[RutaResponse],
    summary="Listar rutas activas",
)
async def listar_rutas_activas(
    use_case: Annotated[ListarRutasActivas, Depends(get_listar_rutas_activas)],
    vehiculo_repo: VehiculoRepo,
) -> list[RutaResponse]:
    rutas = await use_case.ejecutar()
    return [await _a_respuesta(r, vehiculo_repo) for r in rutas]


@router.get(
    "/rutas/{ruta_id}",
    response_model=RutaResponse,
    summary="Obtener una ruta por id",
)
async def obtener_ruta(
    ruta_id: UUID,
    use_case: Annotated[ObtenerRuta, Depends(get_obtener_ruta)],
    vehiculo_repo: VehiculoRepo,
) -> RutaResponse:
    ruta = await use_case.ejecutar(ruta_id)
    return await _a_respuesta(ruta, vehiculo_repo)
