from app.domain.entities import Coordenada
from app.infrastructure.external.ruta_director import RutaDirector

ORIGEN = Coordenada(latitud=4.71, longitud=-74.07)
DESTINO = Coordenada(latitud=6.25, longitud=-75.56)

RUTA_OSRM = {
    "distance": 415000.0,
    "duration": 18000.0,
    "geometry": {"coordinates": [[-74.07, 4.71], [-75.56, 6.25]]},
}


def test_construir_desde_respuesta_osrm_traduce_unidades_y_geometria():
    ruta = RutaDirector().construir_desde_respuesta_osrm(ORIGEN, DESTINO, RUTA_OSRM)

    assert ruta.origen == ORIGEN
    assert ruta.destino == DESTINO
    assert ruta.distancia_km == 415.0
    assert ruta.duracion_min == 300.0
    assert ruta.puntos == [
        Coordenada(latitud=4.71, longitud=-74.07),
        Coordenada(latitud=6.25, longitud=-75.56),
    ]


def test_construir_desde_respuesta_osrm_sin_puntos_intermedios():
    ruta_osrm = {**RUTA_OSRM, "geometry": {"coordinates": []}}

    ruta = RutaDirector().construir_desde_respuesta_osrm(ORIGEN, DESTINO, ruta_osrm)

    assert ruta.puntos == []
