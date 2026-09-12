import httpx
import pytest

from app.domain.entities import Coordenada
from app.domain.exceptions import ProveedorNoDisponible, SinRutaEncontrada
from app.infrastructure.external.osrm_client import OSRMClient

ORIGEN = Coordenada(latitud=4.71, longitud=-74.07)
DESTINO = Coordenada(latitud=6.25, longitud=-75.56)

RESPUESTA_OSRM_OK = {
    "code": "Ok",
    "routes": [
        {
            "distance": 415000.0,
            "duration": 18000.0,
            "geometry": {"coordinates": [[-74.07, 4.71], [-75.56, 6.25]]},
        }
    ],
}


def _client_con_handler(handler) -> httpx.AsyncClient:
    transport = httpx.MockTransport(handler)
    return httpx.AsyncClient(transport=transport)


async def test_calcular_ruta_exitosa_normaliza_la_respuesta():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=RESPUESTA_OSRM_OK)

    osrm = OSRMClient("http://osrm.test", client=_client_con_handler(handler))

    ruta = await osrm.calcular_ruta(ORIGEN, DESTINO)

    assert ruta.distancia_km == 415.0
    assert ruta.duracion_min == 300.0
    assert ruta.puntos == [
        Coordenada(latitud=4.71, longitud=-74.07),
        Coordenada(latitud=6.25, longitud=-75.56),
    ]


async def test_calcular_ruta_sin_camino_lanza_sin_ruta_encontrada():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"code": "NoRoute", "routes": []})

    osrm = OSRMClient("http://osrm.test", client=_client_con_handler(handler))

    with pytest.raises(SinRutaEncontrada):
        await osrm.calcular_ruta(ORIGEN, DESTINO)


async def test_calcular_ruta_con_error_http_lanza_proveedor_no_disponible():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    osrm = OSRMClient("http://osrm.test", client=_client_con_handler(handler))

    with pytest.raises(ProveedorNoDisponible):
        await osrm.calcular_ruta(ORIGEN, DESTINO)


async def test_calcular_ruta_con_proveedor_inalcanzable_lanza_proveedor_no_disponible():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no se pudo conectar", request=request)

    osrm = OSRMClient("http://osrm.test", client=_client_con_handler(handler))

    with pytest.raises(ProveedorNoDisponible):
        await osrm.calcular_ruta(ORIGEN, DESTINO)
