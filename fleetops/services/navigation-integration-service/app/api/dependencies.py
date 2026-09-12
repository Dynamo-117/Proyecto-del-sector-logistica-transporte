from typing import Annotated

from fastapi import Depends, Request

from app.application.ports.navigation import NavigationProvider
from app.application.use_cases.ruta_use_cases import CalcularRuta


def get_navigation_provider(request: Request) -> NavigationProvider:
    return request.app.state.navigation_provider


Provider = Annotated[NavigationProvider, Depends(get_navigation_provider)]


def get_calcular_ruta(provider: Provider) -> CalcularRuta:
    return CalcularRuta(provider)
