from typing import Annotated

from fastapi import Depends, Request

from app.application.facade.resumen_operativo_facade import ResumenOperativoFacade
from app.application.ports.proxy import ProxyClient
from app.application.use_cases.proxy_use_cases import ReenviarPeticion
from app.core.config import get_settings
from app.infrastructure.external.subsistemas_http import (
    ClienteJson,
    FlotaHttp,
    MantenimientoHttp,
    RutasHttp,
    TrackingHttp,
)


def get_proxy_client(request: Request) -> ProxyClient:
    return request.app.state.proxy_client


Proxy = Annotated[ProxyClient, Depends(get_proxy_client)]


def get_reenviar_peticion(proxy_client: Proxy) -> ReenviarPeticion:
    settings = get_settings()
    return ReenviarPeticion(proxy_client, settings.rutas_servicios)


def get_resumen_facade(request: Request) -> ResumenOperativoFacade:
    rutas = get_settings().rutas_servicios
    cliente = ClienteJson(request.app.state.http_client)
    return ResumenOperativoFacade(
        flota=FlotaHttp(cliente, rutas["fleet"]),
        rutas=RutasHttp(cliente, rutas["routing"]),
        mantenimiento=MantenimientoHttp(cliente, rutas["maintenance"]),
        tracking=TrackingHttp(cliente, rutas["tracking"]),
    )
