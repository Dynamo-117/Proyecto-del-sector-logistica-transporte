import httpx
import pytest

from app.domain.exceptions import ServicioNoDisponible
from app.infrastructure.external.httpx_proxy_client import HttpxProxyClient


def _client_con_handler(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_enviar_reenvia_metodo_headers_y_cuerpo():
    peticion_recibida = {}

    def handler(request: httpx.Request) -> httpx.Response:
        peticion_recibida["method"] = request.method
        peticion_recibida["url"] = str(request.url)
        peticion_recibida["header_custom"] = request.headers.get("x-custom")
        peticion_recibida["body"] = request.content
        return httpx.Response(201, json={"ok": True})

    proxy = HttpxProxyClient(_client_con_handler(handler))

    respuesta = await proxy.enviar(
        "POST",
        "http://backend.local/vehiculos",
        {"x-custom": "valor"},
        {"skip": "0"},
        b'{"placa": "ABC123"}',
    )

    assert respuesta.status_code == 201
    assert peticion_recibida["method"] == "POST"
    assert peticion_recibida["url"] == "http://backend.local/vehiculos?skip=0"
    assert peticion_recibida["header_custom"] == "valor"
    assert peticion_recibida["body"] == b'{"placa": "ABC123"}'

    await respuesta.aclose()


async def test_enviar_con_backend_inalcanzable_lanza_servicio_no_disponible():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no se pudo conectar", request=request)

    proxy = HttpxProxyClient(_client_con_handler(handler))

    with pytest.raises(ServicioNoDisponible):
        await proxy.enviar("GET", "http://backend.local/vehiculos", {}, {}, b"")
