from tests.unit.fakes import FakeRespuestaBackend


async def test_health_no_requiere_token(client_sin_auth):
    respuesta = await client_sin_auth.get("/health")

    assert respuesta.status_code == 200


async def test_ready_no_requiere_token(client_sin_auth):
    respuesta = await client_sin_auth.get("/ready")

    assert respuesta.status_code in (200, 503)


async def test_login_no_requiere_token(client_sin_auth, fake_proxy_client):
    fake_proxy_client.respuesta = FakeRespuestaBackend(
        status_code=200, headers={"content-type": "application/json"}, body=b'{"access_token":"x"}'
    )

    respuesta = await client_sin_auth.post(
        "/fleet/auth/login", json={"email": "a@a.com", "password": "x"}
    )

    assert respuesta.status_code == 200


async def test_ruta_protegida_sin_token_devuelve_401(client_sin_auth):
    respuesta = await client_sin_auth.get("/fleet/vehiculos")

    assert respuesta.status_code == 401
    cuerpo = respuesta.json()
    assert cuerpo["codigo"] == "NO_AUTENTICADO"
    assert cuerpo["detalle"] is None


async def test_ruta_protegida_con_token_invalido_devuelve_401(client_sin_auth):
    respuesta = await client_sin_auth.get(
        "/fleet/vehiculos", headers={"Authorization": "Bearer token-basura"}
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "TOKEN_INVALIDO"


async def test_ruta_protegida_con_token_valido_pasa(client, fake_proxy_client):
    respuesta = await client.get("/fleet/vehiculos")

    assert respuesta.status_code == 200
    assert len(fake_proxy_client.llamadas) == 1


async def test_operador_puede_crear_vehiculo(client, fake_proxy_client):
    fake_proxy_client.respuesta = FakeRespuestaBackend(status_code=201)

    respuesta = await client.post("/fleet/vehiculos", json={"placa": "ABC123"})

    assert respuesta.status_code == 201


async def test_operador_puede_asignar_conductor(client, fake_proxy_client):
    vehiculo_id = "11111111-1111-1111-1111-111111111111"
    respuesta = await client.post(f"/fleet/vehiculos/{vehiculo_id}/asignar-conductor", json={})

    assert respuesta.status_code == 200


async def test_operador_no_puede_editar_vehiculo_devuelve_403(client):
    vehiculo_id = "11111111-1111-1111-1111-111111111111"
    respuesta = await client.patch(f"/fleet/vehiculos/{vehiculo_id}", json={"estado": "INACTIVO"})

    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "ROL_NO_AUTORIZADO"


async def test_operador_no_puede_eliminar_vehiculo_devuelve_403(client):
    vehiculo_id = "11111111-1111-1111-1111-111111111111"
    respuesta = await client.delete(f"/fleet/vehiculos/{vehiculo_id}")

    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "ROL_NO_AUTORIZADO"


async def test_operador_no_puede_eliminar_conductor_devuelve_403(client):
    conductor_id = "22222222-2222-2222-2222-222222222222"
    respuesta = await client.delete(f"/fleet/conductores/{conductor_id}")

    assert respuesta.status_code == 403


async def test_administrador_puede_editar_vehiculo(client_admin, fake_proxy_client):
    vehiculo_id = "11111111-1111-1111-1111-111111111111"
    respuesta = await client_admin.patch(
        f"/fleet/vehiculos/{vehiculo_id}", json={"estado": "INACTIVO"}
    )

    assert respuesta.status_code == 200


async def test_administrador_puede_eliminar_vehiculo(client_admin, fake_proxy_client):
    fake_proxy_client.respuesta = FakeRespuestaBackend(status_code=204)
    vehiculo_id = "11111111-1111-1111-1111-111111111111"

    respuesta = await client_admin.delete(f"/fleet/vehiculos/{vehiculo_id}")

    assert respuesta.status_code == 204
