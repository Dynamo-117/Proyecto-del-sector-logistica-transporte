async def test_crear_y_obtener_conductor(client):
    payload = {"nombre": "Juan Perez", "licencia": "LIC-001"}
    respuesta_creacion = await client.post("/conductores", json=payload)

    assert respuesta_creacion.status_code == 201
    creado = respuesta_creacion.json()
    assert creado["nombre"] == "Juan Perez"
    assert creado["estado"] == "DISPONIBLE"

    respuesta_get = await client.get(f"/conductores/{creado['id']}")
    assert respuesta_get.status_code == 200


async def test_crear_conductor_con_licencia_duplicada_devuelve_409(client):
    payload = {"nombre": "Juan Perez", "licencia": "LIC-DUP"}
    await client.post("/conductores", json=payload)
    respuesta = await client.post("/conductores", json={"nombre": "Otro", "licencia": "LIC-DUP"})

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "LICENCIA_DUPLICADA"


async def test_listar_y_eliminar_conductor(client):
    creado = (
        await client.post("/conductores", json={"nombre": "Ana", "licencia": "LIC-500"})
    ).json()

    respuesta_lista = await client.get("/conductores")
    assert respuesta_lista.status_code == 200
    assert len(respuesta_lista.json()) == 1

    respuesta_delete = await client.delete(f"/conductores/{creado['id']}")
    assert respuesta_delete.status_code == 204
