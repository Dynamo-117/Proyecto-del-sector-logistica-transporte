async def test_solicitar_asignacion_sin_vehiculo_disponible_devuelve_409(
    client, dos_nodos_conectados
):
    origen_id, destino_id = dos_nodos_conectados

    respuesta = await client.post(
        "/cargas",
        json={
            "origen_nodo_id": str(origen_id),
            "destino_nodo_id": str(destino_id),
            "peso_kg": 100,
            "volumen_m3": 1,
        },
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "SIN_VEHICULO_DISPONIBLE"


async def test_solicitar_asignacion_exitosa_y_consultar_ruta(
    client, dos_nodos_conectados, vehiculo_disponible
):
    origen_id, destino_id = dos_nodos_conectados

    respuesta = await client.post(
        "/cargas",
        json={
            "origen_nodo_id": str(origen_id),
            "destino_nodo_id": str(destino_id),
            "peso_kg": 100,
            "volumen_m3": 1,
        },
    )

    assert respuesta.status_code == 201
    ruta = respuesta.json()
    assert ruta["vehiculo_id"] == str(vehiculo_disponible)
    assert ruta["vehiculo_placa"] == "ABC123"
    assert ruta["distancia_km"] == 415
    assert ruta["estado"] == "ACTIVA"

    obtenida = await client.get(f"/rutas/{ruta['id']}")
    assert obtenida.status_code == 200

    activas = await client.get("/rutas")
    assert activas.status_code == 200
    assert len(activas.json()) == 1


async def test_obtener_ruta_inexistente_devuelve_404(client):
    respuesta = await client.get("/rutas/11111111-1111-1111-1111-111111111111")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "RUTA_NO_ENCONTRADA"


async def test_solicitar_asignacion_sin_ruta_en_el_grafo_devuelve_422(client, vehiculo_disponible):
    nodo_a = (
        await client.post("/nodos", json={"nombre": "Aislado A", "latitud": 0, "longitud": 0})
    ).json()
    nodo_b = (
        await client.post("/nodos", json={"nombre": "Aislado B", "latitud": 1, "longitud": 1})
    ).json()

    respuesta = await client.post(
        "/cargas",
        json={
            "origen_nodo_id": nodo_a["id"],
            "destino_nodo_id": nodo_b["id"],
            "peso_kg": 100,
            "volumen_m3": 1,
        },
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "SIN_RUTA_EN_GRAFO"
