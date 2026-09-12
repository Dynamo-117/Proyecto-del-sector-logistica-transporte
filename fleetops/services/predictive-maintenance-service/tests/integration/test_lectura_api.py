from uuid import uuid4


async def test_registrar_lectura_de_vehiculo_desconocido_devuelve_404(client):
    respuesta = await client.post(
        "/lecturas", json={"vehiculo_id": str(uuid4()), "kilometraje_km": 100, "horas_motor": 5}
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "VEHICULO_DESCONOCIDO"


async def test_registrar_lectura_sin_alertas(client, vehiculo_conocido):
    respuesta = await client.post(
        "/lecturas",
        json={"vehiculo_id": str(vehiculo_conocido), "kilometraje_km": 100, "horas_motor": 5},
    )

    assert respuesta.status_code == 201
    body = respuesta.json()
    assert body["alertas_generadas"] == []


async def test_registrar_lectura_que_supera_umbral_genera_alerta(client, vehiculo_conocido):
    respuesta = await client.post(
        "/lecturas",
        json={"vehiculo_id": str(vehiculo_conocido), "kilometraje_km": 10_000, "horas_motor": 0},
    )

    assert respuesta.status_code == 201
    alertas = respuesta.json()["alertas_generadas"]
    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "CAMBIO_ACEITE"
    assert alertas[0]["estado"] == "ACTIVA"


async def test_registrar_lectura_con_kilometraje_negativo_devuelve_422(client, vehiculo_conocido):
    respuesta = await client.post(
        "/lecturas",
        json={"vehiculo_id": str(vehiculo_conocido), "kilometraje_km": -1, "horas_motor": 0},
    )

    assert respuesta.status_code == 422
