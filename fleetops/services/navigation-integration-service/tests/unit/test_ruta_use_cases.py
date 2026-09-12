from app.application.use_cases.ruta_use_cases import CalcularRuta
from app.domain.entities import Coordenada, Ruta


class FakeNavigationProvider:
    def __init__(self, ruta: Ruta):
        self._ruta = ruta
        self.llamadas: list[tuple[Coordenada, Coordenada]] = []

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        self.llamadas.append((origen, destino))
        return self._ruta


async def test_calcular_ruta_delega_en_el_proveedor():
    origen = Coordenada(latitud=4.71, longitud=-74.07)
    destino = Coordenada(latitud=6.25, longitud=-75.56)
    ruta_esperada = Ruta(
        origen=origen, destino=destino, distancia_km=415, duracion_min=300, puntos=[]
    )
    provider = FakeNavigationProvider(ruta_esperada)

    ruta = await CalcularRuta(provider).ejecutar(origen, destino)

    assert ruta is ruta_esperada
    assert provider.llamadas == [(origen, destino)]
