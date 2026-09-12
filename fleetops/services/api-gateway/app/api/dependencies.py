from typing import Annotated

from fastapi import Depends, Request

from app.application.ports.proxy import ProxyClient
from app.application.use_cases.proxy_use_cases import ReenviarPeticion
from app.core.config import get_settings


def get_proxy_client(request: Request) -> ProxyClient:
    return request.app.state.proxy_client


Proxy = Annotated[ProxyClient, Depends(get_proxy_client)]


def get_reenviar_peticion(proxy_client: Proxy) -> ReenviarPeticion:
    settings = get_settings()
    return ReenviarPeticion(proxy_client, settings.rutas_servicios)
