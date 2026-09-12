async def test_crear_nodo_y_listar(client):
    respuesta = await client.post(
        "/nodos", json={"nombre": "Bogota", "latitud": 4.71, "longitud": -74.07}
    )

    assert respuesta.status_code == 201
    nodo = respuesta.json()
    assert nodo["nombre"] == "Bogota"

    listado = await client.get("/nodos")
    assert listado.status_code == 200
    assert len(listado.json()) == 1


async def test_crear_conexion_entre_nodos(client):
    origen = (await client.post("/nodos", json={"nombre": "A", "latitud": 0, "longitud": 0})).json()
    destino = (
        await client.post("/nodos", json={"nombre": "B", "latitud": 1, "longitud": 1})
    ).json()

    respuesta = await client.post(
        f"/nodos/{origen['id']}/conexiones",
        json={"nodo_destino_id": destino["id"], "distancia_km": 50},
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["distancia_km"] == 50


async def test_crear_conexion_con_nodo_inexistente_devuelve_404(client):
    origen = (await client.post("/nodos", json={"nombre": "A", "latitud": 0, "longitud": 0})).json()

    respuesta = await client.post(
        f"/nodos/{origen['id']}/conexiones",
        json={"nodo_destino_id": "11111111-1111-1111-1111-111111111111", "distancia_km": 50},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "NODO_NO_ENCONTRADO"
