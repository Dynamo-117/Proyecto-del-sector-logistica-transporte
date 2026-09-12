async def test_asignar_y_desasignar_conductor(client):
    vehiculo = (
        await client.post(
            "/vehiculos", json={"placa": "ASG1", "tipo": "CAMION", "capacidad_kg": 1000}
        )
    ).json()
    conductor = (
        await client.post("/conductores", json={"nombre": "Ana", "licencia": "LIC-ASG"})
    ).json()

    respuesta_asignar = await client.post(
        f"/vehiculos/{vehiculo['id']}/asignar-conductor", json={"conductor_id": conductor["id"]}
    )
    assert respuesta_asignar.status_code == 200
    assert respuesta_asignar.json()["conductor_id"] == conductor["id"]
    assert respuesta_asignar.json()["estado"] == "EN_RUTA"

    respuesta_desasignar = await client.post(f"/vehiculos/{vehiculo['id']}/desasignar-conductor")
    assert respuesta_desasignar.status_code == 200
    assert respuesta_desasignar.json()["conductor_id"] is None
    assert respuesta_desasignar.json()["estado"] == "DISPONIBLE"


async def test_asignar_conductor_ya_ocupado_devuelve_409(client):
    vehiculo1 = (
        await client.post(
            "/vehiculos", json={"placa": "ASG2", "tipo": "CAMION", "capacidad_kg": 1000}
        )
    ).json()
    vehiculo2 = (
        await client.post(
            "/vehiculos", json={"placa": "ASG3", "tipo": "FURGON", "capacidad_kg": 500}
        )
    ).json()
    conductor = (
        await client.post("/conductores", json={"nombre": "Beto", "licencia": "LIC-ASG2"})
    ).json()

    await client.post(
        f"/vehiculos/{vehiculo1['id']}/asignar-conductor", json={"conductor_id": conductor["id"]}
    )
    respuesta = await client.post(
        f"/vehiculos/{vehiculo2['id']}/asignar-conductor", json={"conductor_id": conductor["id"]}
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "CONDUCTOR_NO_DISPONIBLE"
