import pytest

from app.domain.entities import Coordenada
from app.domain.ruta_builder import RutaBuilder

ORIGEN = Coordenada(latitud=4.71, longitud=-74.07)
DESTINO = Coordenada(latitud=6.25, longitud=-75.56)


def test_construir_ensambla_una_ruta_completa():
    ruta = (
        RutaBuilder()
        .con_extremos(ORIGEN, DESTINO)
        .con_metricas(distancia_metros=415000.0, duracion_segundos=18000.0)
        .con_geometria([(-74.07, 4.71), (-75.56, 6.25)])
        .construir()
    )

    assert ruta.origen == ORIGEN
    assert ruta.destino == DESTINO
    assert ruta.distancia_km == 415.0
    assert ruta.duracion_min == 300.0
    assert ruta.puntos == [
        Coordenada(latitud=4.71, longitud=-74.07),
        Coordenada(latitud=6.25, longitud=-75.56),
    ]


def test_con_geometria_es_opcional_y_por_defecto_es_lista_vacia():
    ruta = (
        RutaBuilder()
        .con_extremos(ORIGEN, DESTINO)
        .con_metricas(distancia_metros=1000.0, duracion_segundos=60.0)
        .construir()
    )

    assert ruta.puntos == []


def test_cada_paso_devuelve_el_mismo_builder_para_encadenar():
    builder = RutaBuilder()

    assert builder.con_extremos(ORIGEN, DESTINO) is builder
    assert builder.con_metricas(distancia_metros=1.0, duracion_segundos=1.0) is builder
    assert builder.con_geometria([]) is builder


def test_construir_sin_extremos_lanza_value_error():
    with pytest.raises(ValueError, match="extremos"):
        RutaBuilder().con_metricas(distancia_metros=1.0, duracion_segundos=1.0).construir()


def test_construir_sin_metricas_lanza_value_error():
    with pytest.raises(ValueError, match="metricas"):
        RutaBuilder().con_extremos(ORIGEN, DESTINO).construir()
