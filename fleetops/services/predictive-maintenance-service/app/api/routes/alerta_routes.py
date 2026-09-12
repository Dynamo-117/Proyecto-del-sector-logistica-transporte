from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_listar_alertas_activas, get_marcar_mantenimiento_realizado
from app.api.schemas.alerta_schemas import AlertaResponse
from app.application.use_cases.alerta_use_cases import (
    ListarAlertasActivas,
    MarcarMantenimientoRealizado,
)

router = APIRouter(tags=["alertas"])


@router.get(
    "/vehiculos/{vehiculo_id}/alertas",
    response_model=list[AlertaResponse],
    summary="Listar alertas de mantenimiento activas de un vehiculo",
)
async def listar_alertas_activas(
    vehiculo_id: UUID,
    use_case: Annotated[ListarAlertasActivas, Depends(get_listar_alertas_activas)],
) -> list[AlertaResponse]:
    alertas = await use_case.ejecutar(vehiculo_id)
    return [AlertaResponse.model_validate(a) for a in alertas]


@router.post(
    "/alertas/{alerta_id}/completar",
    response_model=AlertaResponse,
    summary="Marcar una alerta de mantenimiento como realizada",
    description="Resuelve la alerta y reinicia el desgaste de ese tipo desde la ultima lectura.",
)
async def completar_alerta(
    alerta_id: UUID,
    use_case: Annotated[MarcarMantenimientoRealizado, Depends(get_marcar_mantenimiento_realizado)],
) -> AlertaResponse:
    alerta = await use_case.ejecutar(alerta_id)
    return AlertaResponse.model_validate(alerta)
