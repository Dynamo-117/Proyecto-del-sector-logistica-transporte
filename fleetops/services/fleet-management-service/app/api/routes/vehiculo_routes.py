from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import (
    get_actualizar_vehiculo,
    get_crear_vehiculo,
    get_eliminar_vehiculo,
    get_listar_vehiculos,
    get_obtener_vehiculo,
)
from app.api.schemas.vehiculo_schemas import VehiculoCreate, VehiculoResponse, VehiculoUpdate
from app.application.use_cases.vehiculo_use_cases import (
    ActualizarVehiculo,
    CrearVehiculo,
    EliminarVehiculo,
    ListarVehiculos,
    ObtenerVehiculo,
)

router = APIRouter(prefix="/vehiculos", tags=["vehiculos"])


@router.post(
    "",
    response_model=VehiculoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un vehiculo",
    description="Registra un nuevo vehiculo en la flota y publica un evento 'vehiculo.creado'.",
)
async def crear_vehiculo(
    payload: VehiculoCreate,
    use_case: Annotated[CrearVehiculo, Depends(get_crear_vehiculo)],
) -> VehiculoResponse:
    vehiculo = await use_case.ejecutar(payload.placa, payload.tipo, payload.capacidad_kg)
    return VehiculoResponse.model_validate(vehiculo)


@router.get(
    "",
    response_model=list[VehiculoResponse],
    summary="Listar vehiculos",
    description="Devuelve la lista paginada de vehiculos registrados.",
)
async def listar_vehiculos(
    use_case: Annotated[ListarVehiculos, Depends(get_listar_vehiculos)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[VehiculoResponse]:
    vehiculos = await use_case.ejecutar(skip=skip, limit=limit)
    return [VehiculoResponse.model_validate(v) for v in vehiculos]


@router.get(
    "/{vehiculo_id}",
    response_model=VehiculoResponse,
    summary="Obtener un vehiculo por id",
)
async def obtener_vehiculo(
    vehiculo_id: UUID,
    use_case: Annotated[ObtenerVehiculo, Depends(get_obtener_vehiculo)],
) -> VehiculoResponse:
    vehiculo = await use_case.ejecutar(vehiculo_id)
    return VehiculoResponse.model_validate(vehiculo)


@router.patch(
    "/{vehiculo_id}",
    response_model=VehiculoResponse,
    summary="Actualizar un vehiculo",
    description="Actualiza un vehiculo y publica un evento 'vehiculo.actualizado'.",
)
async def actualizar_vehiculo(
    vehiculo_id: UUID,
    payload: VehiculoUpdate,
    use_case: Annotated[ActualizarVehiculo, Depends(get_actualizar_vehiculo)],
) -> VehiculoResponse:
    vehiculo = await use_case.ejecutar(
        vehiculo_id,
        tipo=payload.tipo,
        capacidad_kg=payload.capacidad_kg,
        estado=payload.estado,
    )
    return VehiculoResponse.model_validate(vehiculo)


@router.delete(
    "/{vehiculo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un vehiculo",
)
async def eliminar_vehiculo(
    vehiculo_id: UUID,
    use_case: Annotated[EliminarVehiculo, Depends(get_eliminar_vehiculo)],
) -> None:
    await use_case.ejecutar(vehiculo_id)
