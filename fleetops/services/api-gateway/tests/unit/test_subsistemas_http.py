import httpx
import pytest

from app.domain.exceptions import ServicioNoDisponible
from app.infrastructure.external.subsistemas_http import (
    ClienteJson,
    FlotaHttp,
    MantenimientoHttp,
    TrackingHttp,
)


def _cliente(handler) -> ClienteJson:
    return ClienteJson(httpx.AsyncClient(transport=httpx.MockTransport(handler)))


async def test_devuelve_el_json_de_una_respuesta_correcta():
    cliente = _cliente(lambda r: httpx.Response(200, json=[{"id": "1"}]))

    assert await cliente.obtener("http://x/vehiculos", {}) == [{"id": "1"}]


async def test_un_404_se_convierte_en_none():
    cliente = _cliente(lambda r: httpx.Response(404, json={"codigo": "NO"}))

    assert await cliente.obtener("http://x/vehiculos/1", {}) is None


async def test_un_5xx_lanza_servicio_no_disponible():
    cliente = _cliente(lambda r: httpx.Response(503))

    with pytest.raises(ServicioNoDisponible):
        await cliente.obtener("http://x", {})


async def test_un_error_de_red_lanza_servicio_no_disponible():
    def caido(request):
        raise httpx.ConnectError("sin conexion", request=request)

    with pytest.raises(ServicioNoDisponible):
        await _cliente(caido).obtener("http://x", {})


async def test_flota_http_consulta_vehiculos_en_su_servicio():
    vistas = []

    def handler(request):
        vistas.append(str(request.url))
        return httpx.Response(200, json=[{"id": "1", "estado": "DISPONIBLE"}])

    flota = FlotaHttp(_cliente(handler), "http://fleet")

    assert len(await flota.listar_vehiculos({})) == 1
    assert vistas == ["http://fleet/vehiculos?limit=500"]


async def test_mantenimiento_http_cuenta_las_alertas_y_un_404_es_cero():
    ok = MantenimientoHttp(_cliente(lambda r: httpx.Response(200, json=[{}, {}])), "http://m")
    desconocido = MantenimientoHttp(_cliente(lambda r: httpx.Response(404)), "http://m")

    assert await ok.contar_alertas_activas("1", {}) == 2
    assert await desconocido.contar_alertas_activas("1", {}) == 0


async def test_tracking_http_devuelve_el_estado_o_none_sin_telemetria():
    con = TrackingHttp(
        _cliente(lambda r: httpx.Response(200, json={"estado_movimiento": "DETENIDO"})), "http://t"
    )
    sin = TrackingHttp(_cliente(lambda r: httpx.Response(404)), "http://t")

    assert await con.estado_movimiento("1", {}) == "DETENIDO"
    assert await sin.estado_movimiento("1", {}) is None
