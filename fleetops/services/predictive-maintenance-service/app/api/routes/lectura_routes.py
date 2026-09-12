from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_registrar_lectura
from app.api.schemas.alerta_schemas import AlertaResponse, IngestaConAlertasResponse
from app.api.schemas.lectura_schemas import LecturaOdometroCreate
from app.application.use_cases.lectura_use_cases import RegistrarLecturaOdometro

router = APIRouter(prefix="/lecturas", tags=["lecturas"])


@router.post(
    "",
    response_model=IngestaConAlertasResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una lectura de kilometraje/horas de motor",
    description="Evalua los umbrales de mantenimiento y genera alertas nuevas si corresponde.",
)
async def registrar_lectura(
    payload: LecturaOdometroCreate,
    use_case: Annotated[RegistrarLecturaOdometro, Depends(get_registrar_lectura)],
) -> IngestaConAlertasResponse:
    lectura, alertas = await use_case.ejecutar(
        payload.vehiculo_id, payload.kilometraje_km, payload.horas_motor
    )
    return IngestaConAlertasResponse(
        kilometraje_km=lectura.kilometraje_km,
        horas_motor=lectura.horas_motor,
        alertas_generadas=[AlertaResponse.model_validate(a) for a in alertas],
    )
