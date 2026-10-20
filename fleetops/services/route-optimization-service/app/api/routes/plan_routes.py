from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import AristaRepo, NodoRepo
from app.api.schemas.plan_schemas import PlanRutaRequest, PlanRutaResponse
from app.application.use_cases.plan_use_cases import PlanificarRutaConParadas

router = APIRouter(prefix="/planes", tags=["planes"])


def get_planificar_ruta(nodo_repo: NodoRepo, arista_repo: AristaRepo) -> PlanificarRutaConParadas:
    return PlanificarRutaConParadas(nodo_repo, arista_repo)


@router.post(
    "",
    response_model=PlanRutaResponse,
    summary="Planificar una ruta con varias paradas",
    description=(
        "Calcula el camino mas corto entre cada par de paradas consecutivas y devuelve el "
        "itinerario como arbol: itinerario -> trayectos -> tramos (patron Composite)."
    ),
)
async def planificar_ruta(
    payload: PlanRutaRequest,
    use_case: Annotated[PlanificarRutaConParadas, Depends(get_planificar_ruta)],
) -> PlanRutaResponse:
    itinerario, nombres = await use_case.ejecutar(payload.paradas)
    return PlanRutaResponse(
        distancia_km=itinerario.distancia_km(),
        cantidad_tramos=itinerario.cantidad_tramos(),
        paradas=[nombres[p] for p in payload.paradas],
        nodos=itinerario.nodos(),
        estructura=itinerario.describir(nombres),
    )
