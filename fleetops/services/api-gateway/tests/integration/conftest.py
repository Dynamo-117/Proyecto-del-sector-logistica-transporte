from collections.abc import AsyncGenerator

import httpx
import jwt
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_proxy_client
from app.core.config import get_settings
from app.main import create_app
from tests.unit.fakes import FakeProxyClient


def _crear_token(usuario_id: str, rol: str) -> str:
    settings = get_settings()
    payload = {"sub": usuario_id, "rol": rol}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@pytest_asyncio.fixture
async def token_operador() -> str:
    return _crear_token("11111111-1111-1111-1111-111111111111", "OPERADOR")


@pytest_asyncio.fixture
async def token_administrador() -> str:
    return _crear_token("22222222-2222-2222-2222-222222222222", "ADMINISTRADOR")


@pytest_asyncio.fixture
async def fake_proxy_client() -> FakeProxyClient:
    return FakeProxyClient()


@pytest_asyncio.fixture
async def app(fake_proxy_client):
    fastapi_app = create_app()
    fastapi_app.dependency_overrides[get_proxy_client] = lambda: fake_proxy_client
    # /ready lee request.app.state.http_client directamente (no es un Depends),
    # asi que para probarlo hace falta asignarlo a mano: el lifespan real no
    # corre bajo ASGITransport.
    fastapi_app.state.http_client = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200))
    )
    return fastapi_app


@pytest_asyncio.fixture
async def client(app, token_operador) -> AsyncGenerator[AsyncClient, None]:
    # Lleva un JWT de OPERADOR valido por defecto, para que las pruebas de
    # proxy/health existentes (que no son sobre autenticacion) no se vean
    # bloqueadas por el JWTAuthMiddleware. Las pruebas de auth usan
    # client_sin_auth / client_admin para los casos negativos/de rol.
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token_operador}"}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        yield ac


@pytest_asyncio.fixture
async def client_admin(app, token_administrador) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token_administrador}"}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        yield ac


@pytest_asyncio.fixture
async def client_sin_auth(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
