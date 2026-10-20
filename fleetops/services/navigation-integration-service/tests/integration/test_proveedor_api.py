from app.domain.entities import Coordenada, Ruta

PAYLOAD = {
    "origen": {"latitud": 4.71, "longitud": -74.07},
    "destino": {"latitud": 6.25, "longitud": -75.56},
}


class ProveedorConDistancia:
    def __init__(self, distancia_km: float):
        self._distancia_km = distancia_km

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        return Ruta(
            origen=origen,
            destino=destino,
            distancia_km=self._distancia_km,
            duracion_min=1.0,
            puntos=[origen, destino],
        )


async def test_sin_parametro_usa_el_proveedor_por_defecto(client):
    respuesta = await client.post("/rutas/calcular", json=PAYLOAD)

    assert respuesta.json()["distancia_km"] == 415.0


async def test_el_parametro_proveedor_elige_el_proveedor_indicado(client, app):
    app.state.navigation_providers = {"valhalla": ProveedorConDistancia(420.7)}

    respuesta = await client.post("/rutas/calcular?proveedor=valhalla", json=PAYLOAD)

    assert respuesta.status_code == 200
    assert respuesta.json()["distancia_km"] == 420.7


async def test_proveedor_desconocido_devuelve_422(client):
    respuesta = await client.post("/rutas/calcular?proveedor=google", json=PAYLOAD)

    assert respuesta.status_code == 422
