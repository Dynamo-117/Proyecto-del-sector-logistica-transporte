from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_listar_historico, get_obtener_estado_actual
from app.api.schemas.telemetria_schemas import EstadoActualResponse, TelemetriaResponse
from app.application.use_cases.telemetria_use_cases import (
    ListarHistoricoTelemetria,
    ObtenerEstadoActual,
)

router = APIRouter(prefix="/vehiculos", tags=["vehiculos"])


@router.get(
    "/{vehiculo_id}/estado",
    response_model=EstadoActualResponse,
    summary="Estado actual de un vehiculo",
    description="Devuelve la ultima lectura de telemetria conocida para el vehiculo.",
)
async def obtener_estado_actual(
    vehiculo_id: UUID,
    use_case: Annotated[ObtenerEstadoActual, Depends(get_obtener_estado_actual)],
) -> EstadoActualResponse:
    telemetria = await use_case.ejecutar(vehiculo_id)
    return EstadoActualResponse.model_validate(telemetria)


@router.get(
    "/{vehiculo_id}/historico",
    response_model=list[TelemetriaResponse],
    summary="Historico de telemetria de un vehiculo",
)
async def listar_historico(
    vehiculo_id: UUID,
    use_case: Annotated[ListarHistoricoTelemetria, Depends(get_listar_historico)],
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[TelemetriaResponse]:
    registros = await use_case.ejecutar(
        vehiculo_id, desde=desde, hasta=hasta, skip=skip, limit=limit
    )
    return [TelemetriaResponse.model_validate(r) for r in registros]
