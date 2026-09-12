from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import (
    get_actualizar_conductor,
    get_crear_conductor,
    get_eliminar_conductor,
    get_listar_conductores,
    get_obtener_conductor,
)
from app.api.schemas.conductor_schemas import ConductorCreate, ConductorResponse, ConductorUpdate
from app.application.use_cases.conductor_use_cases import (
    ActualizarConductor,
    CrearConductor,
    EliminarConductor,
    ListarConductores,
    ObtenerConductor,
)

router = APIRouter(prefix="/conductores", tags=["conductores"])


@router.post(
    "",
    response_model=ConductorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un conductor",
)
async def crear_conductor(
    payload: ConductorCreate,
    use_case: Annotated[CrearConductor, Depends(get_crear_conductor)],
) -> ConductorResponse:
    conductor = await use_case.ejecutar(payload.nombre, payload.licencia)
    return ConductorResponse.model_validate(conductor)


@router.get(
    "",
    response_model=list[ConductorResponse],
    summary="Listar conductores",
)
async def listar_conductores(
    use_case: Annotated[ListarConductores, Depends(get_listar_conductores)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[ConductorResponse]:
    conductores = await use_case.ejecutar(skip=skip, limit=limit)
    return [ConductorResponse.model_validate(c) for c in conductores]


@router.get(
    "/{conductor_id}",
    response_model=ConductorResponse,
    summary="Obtener un conductor por id",
)
async def obtener_conductor(
    conductor_id: UUID,
    use_case: Annotated[ObtenerConductor, Depends(get_obtener_conductor)],
) -> ConductorResponse:
    conductor = await use_case.ejecutar(conductor_id)
    return ConductorResponse.model_validate(conductor)


@router.patch(
    "/{conductor_id}",
    response_model=ConductorResponse,
    summary="Actualizar un conductor",
)
async def actualizar_conductor(
    conductor_id: UUID,
    payload: ConductorUpdate,
    use_case: Annotated[ActualizarConductor, Depends(get_actualizar_conductor)],
) -> ConductorResponse:
    conductor = await use_case.ejecutar(conductor_id, nombre=payload.nombre, estado=payload.estado)
    return ConductorResponse.model_validate(conductor)


@router.delete(
    "/{conductor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un conductor",
)
async def eliminar_conductor(
    conductor_id: UUID,
    use_case: Annotated[EliminarConductor, Depends(get_eliminar_conductor)],
) -> None:
    await use_case.ejecutar(conductor_id)
