async def test_crear_y_obtener_vehiculo(client, fake_publisher):
    payload = {"placa": "ABC123", "tipo": "CAMION", "capacidad_kg": 1000}
    respuesta_creacion = await client.post("/vehiculos", json=payload)

    assert respuesta_creacion.status_code == 201
    creado = respuesta_creacion.json()
    assert creado["placa"] == "ABC123"
    assert creado["estado"] == "DISPONIBLE"
    assert len(fake_publisher.eventos) == 1

    respuesta_get = await client.get(f"/vehiculos/{creado['id']}")
    assert respuesta_get.status_code == 200
    assert respuesta_get.json()["placa"] == "ABC123"


async def test_crear_vehiculo_con_placa_duplicada_devuelve_409(client):
    payload = {"placa": "XYZ999", "tipo": "FURGON", "capacidad_kg": 500}
    await client.post("/vehiculos", json=payload)
    respuesta = await client.post("/vehiculos", json=payload)

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "PLACA_DUPLICADA"


async def test_obtener_vehiculo_inexistente_devuelve_404(client):
    respuesta = await client.get("/vehiculos/11111111-1111-1111-1111-111111111111")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "VEHICULO_NO_ENCONTRADO"


async def test_crear_vehiculo_con_payload_invalido_devuelve_422(client):
    respuesta = await client.post(
        "/vehiculos", json={"placa": "AB", "tipo": "CAMION", "capacidad_kg": -1}
    )

    assert respuesta.status_code == 422


async def test_listar_vehiculos(client):
    r1 = await client.post(
        "/vehiculos", json={"placa": "LST001", "tipo": "MOTO", "capacidad_kg": 20}
    )
    r2 = await client.post(
        "/vehiculos", json={"placa": "LST002", "tipo": "VAN", "capacidad_kg": 300}
    )
    assert r1.status_code == 201
    assert r2.status_code == 201

    respuesta = await client.get("/vehiculos")

    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 2


async def test_actualizar_y_eliminar_vehiculo(client):
    creado = (
        await client.post(
            "/vehiculos", json={"placa": "DEL1", "tipo": "CAMION", "capacidad_kg": 100}
        )
    ).json()

    respuesta_update = await client.patch(
        f"/vehiculos/{creado['id']}", json={"estado": "MANTENIMIENTO"}
    )
    assert respuesta_update.status_code == 200
    assert respuesta_update.json()["estado"] == "MANTENIMIENTO"

    respuesta_delete = await client.delete(f"/vehiculos/{creado['id']}")
    assert respuesta_delete.status_code == 204

    respuesta_get = await client.get(f"/vehiculos/{creado['id']}")
    assert respuesta_get.status_code == 404
