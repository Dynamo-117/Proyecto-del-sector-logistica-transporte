import pytest

from app.application.use_cases.proxy_use_cases import ReenviarPeticion
from app.domain.exceptions import ServicioNoRegistrado
from tests.unit.fakes import FakeProxyClient


async def test_reenviar_a_prefijo_desconocido_falla():
    proxy_client = FakeProxyClient()
    use_case = ReenviarPeticion(proxy_client, rutas_servicios={"fleet": "http://fleet.local"})

    with pytest.raises(ServicioNoRegistrado):
        await use_case.ejecutar("desconocido", "vehiculos", "GET", {}, {}, b"")

    assert proxy_client.llamadas == []


async def test_reenviar_arma_la_url_con_el_resto_del_path():
    proxy_client = FakeProxyClient()
    use_case = ReenviarPeticion(proxy_client, rutas_servicios={"fleet": "http://fleet.local"})

    await use_case.ejecutar("fleet", "vehiculos/123", "GET", {"a": "1"}, {"skip": "0"}, b"cuerpo")

    assert proxy_client.llamadas == [
        ("GET", "http://fleet.local/vehiculos/123", {"a": "1"}, {"skip": "0"}, b"cuerpo")
    ]


async def test_reenviar_sin_resto_de_path_usa_la_base_url_directamente():
    proxy_client = FakeProxyClient()
    use_case = ReenviarPeticion(proxy_client, rutas_servicios={"fleet": "http://fleet.local"})

    await use_case.ejecutar("fleet", "", "GET", {}, {}, b"")

    assert proxy_client.llamadas[0][1] == "http://fleet.local"
