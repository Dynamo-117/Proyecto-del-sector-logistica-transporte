PAYLOAD = {
    "origen": {"latitud": 4.71, "longitud": -74.07},
    "destino": {"latitud": 6.25, "longitud": -75.56},
}


async def test_calcular_ruta_exitosa(client):
    respuesta = await client.post("/rutas/calcular", json=PAYLOAD)

    assert respuesta.status_code == 200
    body = respuesta.json()
    assert body["distancia_km"] == 415.0
    assert body["duracion_min"] == 300.0


async def test_calcular_ruta_con_coordenada_invalida_devuelve_422(client):
    payload_invalido = {
        "origen": {"latitud": 999, "longitud": -74.07},
        "destino": {"latitud": 6.25, "longitud": -75.56},
    }

    respuesta = await client.post("/rutas/calcular", json=payload_invalido)

    assert respuesta.status_code == 422


async def test_calcular_ruta_sin_camino_devuelve_422(client, fake_provider):
    fake_provider.forzar_sin_ruta = True

    respuesta = await client.post("/rutas/calcular", json=PAYLOAD)

    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "SIN_RUTA_ENCONTRADA"


async def test_calcular_ruta_con_proveedor_caido_devuelve_503(client, fake_provider):
    fake_provider.forzar_no_disponible = True

    respuesta = await client.post("/rutas/calcular", json=PAYLOAD)

    assert respuesta.status_code == 503
    assert respuesta.json()["codigo"] == "PROVEEDOR_NO_DISPONIBLE"
