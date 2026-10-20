import json


async def _sembrar(client):
    conductor = (
        await client.post("/conductores", json={"nombre": "Camila Ruiz", "licencia": "LIC-4471"})
    ).json()
    vehiculo = (
        await client.post(
            "/vehiculos", json={"placa": "VAN042", "tipo": "VAN", "capacidad_kg": 600}
        )
    ).json()
    await client.post(
        f"/vehiculos/{vehiculo['id']}/asignar-conductor", json={"conductor_id": conductor["id"]}
    )


async def test_reporte_csv_se_descarga_como_archivo(client):
    await _sembrar(client)

    respuesta = await client.get("/reportes/vehiculos?formato=csv")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/csv")
    assert 'filename="vehiculos.csv"' in respuesta.headers["content-disposition"]
    assert "VAN042,VAN,600,EN_RUTA,Camila Ruiz" in respuesta.text


async def test_reporte_json_y_html_del_mismo_tipo(client):
    await _sembrar(client)

    como_json = await client.get("/reportes/conductores?formato=json")
    como_html = await client.get("/reportes/conductores?formato=html&descargar=false")

    assert json.loads(como_json.text)["filas"][0]["Nombre"] == "Camila Ruiz"
    assert "<td>Camila Ruiz</td>" in como_html.text
    assert "content-disposition" not in como_html.headers


async def test_resumen_de_flota(client):
    await _sembrar(client)

    respuesta = await client.get("/reportes/resumen?formato=json")

    filas = {f["Estado"]: f for f in json.loads(respuesta.text)["filas"]}
    assert filas["EN_RUTA"]["Vehiculos"] == "1"


async def test_formato_invalido_devuelve_422(client):
    respuesta = await client.get("/reportes/vehiculos?formato=pdf")

    assert respuesta.status_code == 422


async def test_tipo_desconocido_devuelve_404(client):
    respuesta = await client.get("/reportes/inexistente")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "REPORTE_NO_SOPORTADO"
