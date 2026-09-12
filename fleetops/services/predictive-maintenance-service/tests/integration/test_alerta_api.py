from uuid import uuid4


async def test_listar_alertas_de_vehiculo_desconocido_devuelve_404(client):
    respuesta = await client.get(f"/vehiculos/{uuid4()}/alertas")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "VEHICULO_DESCONOCIDO"


async def test_listar_y_completar_alerta(client, vehiculo_conocido):
    await client.post(
        "/lecturas",
        json={"vehiculo_id": str(vehiculo_conocido), "kilometraje_km": 10_000, "horas_motor": 0},
    )

    listado = await client.get(f"/vehiculos/{vehiculo_conocido}/alertas")
    assert listado.status_code == 200
    assert len(listado.json()) == 1
    alerta_id = listado.json()[0]["id"]

    completada = await client.post(f"/alertas/{alerta_id}/completar")
    assert completada.status_code == 200
    assert completada.json()["estado"] == "RESUELTA"

    listado_tras_completar = await client.get(f"/vehiculos/{vehiculo_conocido}/alertas")
    assert listado_tras_completar.json() == []


async def test_completar_alerta_inexistente_devuelve_404(client):
    respuesta = await client.post(f"/alertas/{uuid4()}/completar")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "ALERTA_NO_ENCONTRADA"


async def test_completar_alerta_dos_veces_devuelve_409(client, vehiculo_conocido):
    await client.post(
        "/lecturas",
        json={"vehiculo_id": str(vehiculo_conocido), "kilometraje_km": 10_000, "horas_motor": 0},
    )
    listado = await client.get(f"/vehiculos/{vehiculo_conocido}/alertas")
    alerta_id = listado.json()[0]["id"]

    await client.post(f"/alertas/{alerta_id}/completar")
    segunda_vez = await client.post(f"/alertas/{alerta_id}/completar")

    assert segunda_vez.status_code == 409
    assert segunda_vez.json()["codigo"] == "ALERTA_YA_RESUELTA"


async def test_no_genera_nueva_alerta_hasta_superar_umbral_desde_el_mantenimiento(
    client, vehiculo_conocido
):
    await client.post(
        "/lecturas",
        json={"vehiculo_id": str(vehiculo_conocido), "kilometraje_km": 10_000, "horas_motor": 0},
    )
    alerta_id = (await client.get(f"/vehiculos/{vehiculo_conocido}/alertas")).json()[0]["id"]
    await client.post(f"/alertas/{alerta_id}/completar")

    respuesta = await client.post(
        "/lecturas",
        json={"vehiculo_id": str(vehiculo_conocido), "kilometraje_km": 15_000, "horas_motor": 0},
    )
    assert respuesta.json()["alertas_generadas"] == []

    # A los 20.000 km se cumplen a la vez el segundo ciclo de CAMBIO_ACEITE
    # (base 10.000 + 10.000) y el primer ciclo de REVISION_GENERAL (base 0 +
    # 20.000, nunca reiniciada): es correcto que se generen ambas alertas.
    respuesta_final = await client.post(
        "/lecturas",
        json={"vehiculo_id": str(vehiculo_conocido), "kilometraje_km": 20_000, "horas_motor": 0},
    )
    tipos_generados = {a["tipo"] for a in respuesta_final.json()["alertas_generadas"]}
    assert tipos_generados == {"CAMBIO_ACEITE", "REVISION_GENERAL"}
