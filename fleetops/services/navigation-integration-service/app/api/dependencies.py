from typing import Annotated, Literal

from fastapi import Depends, Query, Request

from app.application.ports.navigation import NavigationProvider
from app.application.use_cases.ruta_use_cases import CalcularRuta


def get_navigation_provider(request: Request) -> NavigationProvider:
    return request.app.state.navigation_provider


Provider = Annotated[NavigationProvider, Depends(get_navigation_provider)]


NombreProveedor = Literal["osrm", "valhalla"]


def get_proveedor_seleccionado(
    request: Request,
    por_defecto: Provider,
    proveedor: Annotated[NombreProveedor | None, Query()] = None,
) -> NavigationProvider:
    if proveedor is None:
        return por_defecto
    return request.app.state.navigation_providers[proveedor]


ProviderSeleccionado = Annotated[NavigationProvider, Depends(get_proveedor_seleccionado)]


def get_calcular_ruta(provider: ProviderSeleccionado) -> CalcularRuta:
    return CalcularRuta(provider)
