import httpx
import pytest

from app.application.use_cases.ruta_use_cases import CalcularRuta
from app.domain.entities import Coordenada
from app.domain.exceptions import ProveedorNoDisponible, SinRutaEncontrada
from app.infrastructure.external.valhalla_adapter import (
    ValhallaNavigationAdapter,
    decodificar_polyline,
)
from app.infrastructure.external.valhalla_api import ValhallaApi

ORIGEN = Coordenada(latitud=4.71, longitud=-74.07)
DESTINO = Coordenada(latitud=6.25, longitud=-75.56)

# Polyline de precision 6 equivalente a [(4.71, -74.07), (6.25, -75.56)].
POLYLINE6 = "_fn~G~}zglC_y~|A~c}yA"

RESPUESTA_VALHALLA_OK = {
    "trip": {
        "summary": {"length": 420.674, "time": 30540.0},
        "legs": [{"shape": POLYLINE6}],
        "status": 0,
    }
}


def _adaptador(handler) -> ValhallaNavigationAdapter:
    cliente = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return ValhallaNavigationAdapter(ValhallaApi("http://valhalla.test", client=cliente))


def test_decodificar_polyline_precision_5_ejemplo_de_google():
    puntos = decodificar_polyline("_p~iF~ps|U_ulLnnqC_mqNvxq`@", precision=5)

    assert puntos == [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)]


def test_decodificar_polyline_precision_6():
    puntos = decodificar_polyline(POLYLINE6, precision=6)

    assert puntos == [(4.71, -74.07), (6.25, -75.56)]


async def test_traduce_la_respuesta_de_valhalla_a_la_ruta_del_dominio():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/route"
        return httpx.Response(200, json=RESPUESTA_VALHALLA_OK)

    ruta = await _adaptador(handler).calcular_ruta(ORIGEN, DESTINO)

    assert ruta.origen == ORIGEN
    assert ruta.destino == DESTINO
    assert ruta.distancia_km == pytest.approx(420.674)
    assert ruta.duracion_min == pytest.approx(509.0)
    assert ruta.puntos == [
        Coordenada(latitud=4.71, longitud=-74.07),
        Coordenada(latitud=6.25, longitud=-75.56),
    ]


async def test_el_caso_de_uso_usa_el_adaptador_sin_saber_que_es_valhalla():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=RESPUESTA_VALHALLA_OK)

    ruta = await CalcularRuta(_adaptador(handler)).ejecutar(ORIGEN, DESTINO)

    assert ruta.distancia_km == pytest.approx(420.674)


async def test_error_4xx_de_valhalla_se_traduce_a_sin_ruta_encontrada():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error_code": 442, "error": "No path could be found"})

    with pytest.raises(SinRutaEncontrada):
        await _adaptador(handler).calcular_ruta(ORIGEN, DESTINO)


async def test_error_5xx_de_valhalla_se_traduce_a_proveedor_no_disponible():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="mantenimiento")

    with pytest.raises(ProveedorNoDisponible):
        await _adaptador(handler).calcular_ruta(ORIGEN, DESTINO)


async def test_proveedor_inalcanzable_se_traduce_a_proveedor_no_disponible():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sin conexion", request=request)

    with pytest.raises(ProveedorNoDisponible):
        await _adaptador(handler).calcular_ruta(ORIGEN, DESTINO)
