from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.infrastructure.messaging.publicador_proxy import PublicadorEventosProxy

router = APIRouter(prefix="/eventos", tags=["eventos"])


class EstadoEventosResponse(BaseModel):
    conectado: bool
    pendientes: int
    publicados: int
    descartados: int


class ReintentoResponse(BaseModel):
    entregados: int
    pendientes: int


def get_publicador_proxy(request: Request) -> PublicadorEventosProxy:
    return request.app.state.event_publisher


ProxyDep = Annotated[PublicadorEventosProxy, Depends(get_publicador_proxy)]


def _estado(proxy: PublicadorEventosProxy) -> EstadoEventosResponse:
    return EstadoEventosResponse(
        conectado=proxy.esta_conectado,
        pendientes=proxy.pendientes,
        publicados=proxy.publicados,
        descartados=proxy.descartados,
    )


@router.get(
    "/estado",
    response_model=EstadoEventosResponse,
    summary="Estado de la mensajeria",
    description="Si RabbitMQ esta conectado y cuantos eventos esperan para ser entregados.",
)
async def estado_eventos(proxy: ProxyDep) -> EstadoEventosResponse:
    return _estado(proxy)


@router.post(
    "/reintentar",
    response_model=ReintentoResponse,
    summary="Reintentar la entrega de los eventos pendientes",
)
async def reintentar_eventos(proxy: ProxyDep) -> ReintentoResponse:
    entregados = await proxy.entregar_pendientes(forzar=True)
    return ReintentoResponse(entregados=entregados, pendientes=proxy.pendientes)
