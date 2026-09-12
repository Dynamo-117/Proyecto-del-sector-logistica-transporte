from uuid import uuid4


async def test_estado_actual_de_vehiculo_desconocido_devuelve_404(client):
    respuesta = await client.get(f"/vehiculos/{uuid4()}/estado")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "VEHICULO_DESCONOCIDO"


async def test_estado_actual_sin_telemetria_devuelve_404(client, vehiculo_conocido):
    respuesta = await client.get(f"/vehiculos/{vehiculo_conocido}/estado")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "TELEMETRIA_NO_DISPONIBLE"


async def test_estado_actual_y_historico(client, vehiculo_conocido):
    await client.post(
        "/telemetria",
        json={
            "vehiculo_id": str(vehiculo_conocido),
            "latitud": 4.71,
            "longitud": -74.07,
            "velocidad_kmh": 10,
        },
    )
    await client.post(
        "/telemetria",
        json={
            "vehiculo_id": str(vehiculo_conocido),
            "latitud": 4.72,
            "longitud": -74.08,
            "velocidad_kmh": 0,
        },
    )

    estado = await client.get(f"/vehiculos/{vehiculo_conocido}/estado")
    assert estado.status_code == 200
    assert estado.json()["estado_movimiento"] == "DETENIDO"

    historico = await client.get(f"/vehiculos/{vehiculo_conocido}/historico")
    assert historico.status_code == 200
    assert len(historico.json()) == 2
