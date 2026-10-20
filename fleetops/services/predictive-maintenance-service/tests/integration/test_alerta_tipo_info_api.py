async def test_las_alertas_traen_el_estado_compartido_de_su_tipo(client, vehiculo_conocido):
    registro = await client.post(
        "/lecturas",
        json={"vehiculo_id": str(vehiculo_conocido), "kilometraje_km": 25_000, "horas_motor": 100},
    )
    listado = await client.get(f"/vehiculos/{vehiculo_conocido}/alertas")

    assert registro.status_code == 201
    por_tipo = {a["tipo"]: a["tipo_info"] for a in listado.json()}
    assert por_tipo["CAMBIO_ACEITE"]["nombre"] == "Cambio de aceite"
    assert por_tipo["CAMBIO_ACEITE"]["prioridad"] == "MEDIA"
    assert por_tipo["REVISION_GENERAL"]["prioridad"] == "ALTA"
    assert por_tipo["REVISION_GENERAL"]["recomendacion"]
    assert registro.json()["alertas_generadas"][0]["tipo_info"]["descripcion"]
