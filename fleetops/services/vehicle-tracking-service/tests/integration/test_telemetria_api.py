from uuid import uuid4


async def test_ingestar_telemetria_de_vehiculo_desconocido_devuelve_404(client):
    payload = {
        "vehiculo_id": str(uuid4()),
        "latitud": 4.71,
        "longitud": -74.07,
        "velocidad_kmh": 20,
    }

    respuesta = await client.post("/telemetria", json=payload)

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "VEHICULO_DESCONOCIDO"


async def test_ingestar_telemetria_de_vehiculo_conocido(client, vehiculo_conocido):
    payload = {
        "vehiculo_id": str(vehiculo_conocido),
        "latitud": 4.71,
        "longitud": -74.07,
        "velocidad_kmh": 55,
    }

    respuesta = await client.post("/telemetria", json=payload)

    assert respuesta.status_code == 201
    body = respuesta.json()
    assert body["vehiculo_id"] == str(vehiculo_conocido)
    assert body["velocidad_kmh"] == 55


async def test_ingestar_telemetria_con_latitud_fuera_de_rango_devuelve_422(
    client, vehiculo_conocido
):
    payload = {
        "vehiculo_id": str(vehiculo_conocido),
        "latitud": 999,
        "longitud": -74.07,
        "velocidad_kmh": 10,
    }

    respuesta = await client.post("/telemetria", json=payload)

    assert respuesta.status_code == 422
