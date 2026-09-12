from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_crear_conexion, get_crear_nodo, get_listar_nodos
from app.api.schemas.grafo_schemas import ConexionCreate, ConexionResponse, NodoCreate, NodoResponse
from app.application.use_cases.grafo_use_cases import CrearConexion, CrearNodo, ListarNodos

router = APIRouter(prefix="/nodos", tags=["grafo"])


@router.post(
    "",
    response_model=NodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nodo del grafo de rutas",
    description="Un punto (ciudad, bodega, cruce) usable como origen/destino de una carga.",
)
async def crear_nodo(
    payload: NodoCreate, use_case: Annotated[CrearNodo, Depends(get_crear_nodo)]
) -> NodoResponse:
    nodo = await use_case.ejecutar(payload.nombre, payload.latitud, payload.longitud)
    return NodoResponse.model_validate(nodo)


@router.get("", response_model=list[NodoResponse], summary="Listar nodos del grafo")
async def listar_nodos(
    use_case: Annotated[ListarNodos, Depends(get_listar_nodos)]
) -> list[NodoResponse]:
    nodos = await use_case.ejecutar()
    return [NodoResponse.model_validate(n) for n in nodos]


@router.post(
    "/{nodo_origen_id}/conexiones",
    response_model=ConexionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una conexion (arista) entre dos nodos",
    description="Bidireccional: se puede recorrer en ambos sentidos con el mismo costo.",
)
async def crear_conexion(
    nodo_origen_id: UUID,
    payload: ConexionCreate,
    use_case: Annotated[CrearConexion, Depends(get_crear_conexion)],
) -> ConexionResponse:
    arista = await use_case.ejecutar(nodo_origen_id, payload.nodo_destino_id, payload.distancia_km)
    return ConexionResponse.model_validate(arista)
