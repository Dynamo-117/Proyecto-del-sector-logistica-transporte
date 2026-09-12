from tests.unit.fakes import FakeRespuestaBackend


async def test_proxy_reenvia_al_servicio_correcto(client, fake_proxy_client):
    fake_proxy_client.respuesta = FakeRespuestaBackend(
        status_code=201, headers={"content-type": "application/json"}, body=b'{"id": "1"}'
    )

    respuesta = await client.post("/fleet/vehiculos", json={"placa": "ABC123"})

    assert respuesta.status_code == 201
    assert respuesta.content == b'{"id": "1"}'

    metodo, url, headers, params, body = fake_proxy_client.llamadas[0]
    assert metodo == "POST"
    assert url == "http://localhost:8000/vehiculos"


async def test_proxy_con_prefijo_desconocido_devuelve_404(client):
    respuesta = await client.get("/inexistente/algo")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "SERVICIO_NO_REGISTRADO"


async def test_proxy_propaga_query_params(client, fake_proxy_client):
    await client.get("/fleet/vehiculos", params={"skip": "10", "limit": "5"})

    _, _, _, params, _ = fake_proxy_client.llamadas[0]
    assert params == {"skip": "10", "limit": "5"}


async def test_proxy_genera_y_propaga_correlation_id(client, fake_proxy_client):
    respuesta = await client.get("/routing/rutas")

    correlation_id_respuesta = respuesta.headers["x-correlation-id"]
    _, _, headers_reenviados, _, _ = fake_proxy_client.llamadas[0]

    assert headers_reenviados["x-correlation-id"] == correlation_id_respuesta


async def test_proxy_respeta_correlation_id_entrante(client, fake_proxy_client):
    respuesta = await client.get("/routing/rutas", headers={"X-Correlation-Id": "mi-id-de-prueba"})

    assert respuesta.headers["x-correlation-id"] == "mi-id-de-prueba"
    _, _, headers_reenviados, _, _ = fake_proxy_client.llamadas[0]
    assert headers_reenviados["x-correlation-id"] == "mi-id-de-prueba"


async def test_proxy_sin_path_adicional_usa_solo_el_prefijo(client, fake_proxy_client):
    await client.get("/navigation")

    _, url, _, _, _ = fake_proxy_client.llamadas[0]
    assert url == "http://localhost:8005"
