from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_navigation_provider
from app.domain.entities import Coordenada, Ruta
from app.domain.exceptions import ProveedorNoDisponible, SinRutaEncontrada
from app.main import create_app


class FakeNavigationProvider:
    def __init__(self):
        self.forzar_sin_ruta = False
        self.forzar_no_disponible = False

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        if self.forzar_sin_ruta:
            raise SinRutaEncontrada("sin camino en la prueba")
        if self.forzar_no_disponible:
            raise ProveedorNoDisponible("proveedor caido en la prueba")

        return Ruta(
            origen=origen,
            destino=destino,
            distancia_km=415.0,
            duracion_min=300.0,
            puntos=[origen, destino],
        )


@pytest_asyncio.fixture
async def fake_provider() -> FakeNavigationProvider:
    return FakeNavigationProvider()


@pytest_asyncio.fixture
async def app(fake_provider):
    fastapi_app = create_app()
    fastapi_app.dependency_overrides[get_navigation_provider] = lambda: fake_provider
    return fastapi_app


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
