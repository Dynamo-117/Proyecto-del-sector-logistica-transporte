from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_ingestar_telemetria
from app.api.schemas.telemetria_schemas import TelemetriaIngesta, TelemetriaResponse
from app.application.use_cases.telemetria_use_cases import IngestarTelemetria

router = APIRouter(prefix="/telemetria", tags=["telemetria"])


@router.post(
    "",
    response_model=TelemetriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingestar un punto de telemetria",
    description=(
        "Registra una lectura de posicion/velocidad de un vehiculo ya conocido "
        "(notificado previamente por fleet-management-service) y la transmite "
        "en tiempo real a quienes esten suscritos via SSE."
    ),
)
async def ingestar_telemetria(
    payload: TelemetriaIngesta,
    use_case: Annotated[IngestarTelemetria, Depends(get_ingestar_telemetria)],
) -> TelemetriaResponse:
    telemetria = await use_case.ejecutar(
        payload.vehiculo_id,
        payload.latitud,
        payload.longitud,
        payload.velocidad_kmh,
        timestamp=payload.timestamp,
    )
    return TelemetriaResponse.model_validate(telemetria)
