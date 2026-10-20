async def _nodo(client, nombre):
    return (
        await client.post("/nodos", json={"nombre": nombre, "latitud": 0, "longitud": 0})
    ).json()


async def _conectar(client, origen, destino, km):
    await client.post(
        f"/nodos/{origen['id']}/conexiones",
        json={"nodo_destino_id": destino["id"], "distancia_km": km},
    )


async def test_planificar_ruta_con_paradas_devuelve_el_arbol(client):
    a, b, c = [await _nodo(client, n) for n in ("Bogota", "Tunja", "Bucaramanga")]
    await _conectar(client, a, b, 150)
    await _conectar(client, b, c, 280)

    respuesta = await client.post("/planes", json={"paradas": [a["id"], b["id"], c["id"]]})

    assert respuesta.status_code == 200
    plan = respuesta.json()
    assert plan["distancia_km"] == 430
    assert plan["cantidad_tramos"] == 2
    assert plan["paradas"] == ["Bogota", "Tunja", "Bucaramanga"]
    assert plan["estructura"]["tipo"] == "trayecto"
    assert [h["nombre"] for h in plan["estructura"]["hijos"]] == [
        "Bogota -> Tunja",
        "Tunja -> Bucaramanga",
    ]
    assert plan["estructura"]["hijos"][0]["hijos"][0]["tipo"] == "tramo"


async def test_plan_con_una_sola_parada_devuelve_422(client):
    a = await _nodo(client, "Bogota")

    respuesta = await client.post("/planes", json={"paradas": [a["id"]]})

    assert respuesta.status_code == 422


async def test_plan_con_paradas_repetidas_devuelve_422(client):
    a = await _nodo(client, "Bogota")

    respuesta = await client.post("/planes", json={"paradas": [a["id"], a["id"]]})

    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "PLAN_INVALIDO"


async def test_plan_sin_camino_devuelve_422(client):
    a, b = await _nodo(client, "A"), await _nodo(client, "B")

    respuesta = await client.post("/planes", json={"paradas": [a["id"], b["id"]]})

    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "SIN_RUTA_EN_GRAFO"
