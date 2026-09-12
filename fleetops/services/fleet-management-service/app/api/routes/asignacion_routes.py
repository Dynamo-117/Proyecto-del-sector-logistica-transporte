from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_asignar_conductor, get_desasignar_conductor
from app.api.schemas.asignacion_schemas import AsignacionRequest
from app.api.schemas.vehiculo_schemas import VehiculoResponse
from app.application.use_cases.asignacion_use_cases import (
    AsignarConductorAVehiculo,
    DesasignarConductorDeVehiculo,
)

router = APIRouter(prefix="/vehiculos", tags=["asignaciones"])


@router.post(
    "/{vehiculo_id}/asignar-conductor",
    response_model=VehiculoResponse,
    summary="Asignar un conductor a un vehiculo",
    description=(
        "Asigna un conductor disponible a un vehiculo disponible. "
        "Es idempotente si se repite la misma asignacion, y falla con 409 "
        "si el vehiculo o el conductor ya estan comprometidos en otra asignacion."
    ),
)
async def asignar_conductor(
    vehiculo_id: UUID,
    payload: AsignacionRequest,
    use_case: Annotated[AsignarConductorAVehiculo, Depends(get_asignar_conductor)],
) -> VehiculoResponse:
    vehiculo = await use_case.ejecutar(vehiculo_id, payload.conductor_id)
    return VehiculoResponse.model_validate(vehiculo)


@router.post(
    "/{vehiculo_id}/desasignar-conductor",
    response_model=VehiculoResponse,
    summary="Desasignar el conductor de un vehiculo",
)
async def desasignar_conductor(
    vehiculo_id: UUID,
    use_case: Annotated[DesasignarConductorDeVehiculo, Depends(get_desasignar_conductor)],
) -> VehiculoResponse:
    vehiculo = await use_case.ejecutar(vehiculo_id)
    return VehiculoResponse.model_validate(vehiculo)
