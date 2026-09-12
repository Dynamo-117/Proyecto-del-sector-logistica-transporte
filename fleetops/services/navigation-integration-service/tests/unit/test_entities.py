import pytest

from app.domain.entities import Coordenada
from app.domain.exceptions import CoordenadaInvalida


def test_coordenada_valida():
    coordenada = Coordenada(latitud=4.71, longitud=-74.07)

    assert coordenada.latitud == 4.71
    assert coordenada.longitud == -74.07


@pytest.mark.parametrize("latitud", [90.1, -90.1, 999])
def test_coordenada_con_latitud_invalida_falla(latitud):
    with pytest.raises(CoordenadaInvalida):
        Coordenada(latitud=latitud, longitud=0)


@pytest.mark.parametrize("longitud", [180.1, -180.1, 999])
def test_coordenada_con_longitud_invalida_falla(longitud):
    with pytest.raises(CoordenadaInvalida):
        Coordenada(latitud=0, longitud=longitud)
