from uuid import uuid4

import pytest

from app.domain.entities import Arista
from app.domain.exceptions import SinRutaEnGrafo
from app.domain.grafo import calcular_ruta_mas_corta


def test_ruta_directa_entre_dos_nodos():
    a, b = uuid4(), uuid4()
    aristas = [Arista(nodo_origen_id=a, nodo_destino_id=b, distancia_km=10)]

    camino, distancia = calcular_ruta_mas_corta(aristas, a, b)

    assert camino == [a, b]
    assert distancia == 10


def test_elige_el_camino_mas_corto_entre_varias_opciones():
    a, b, c, d = uuid4(), uuid4(), uuid4(), uuid4()
    aristas = [
        Arista(nodo_origen_id=a, nodo_destino_id=b, distancia_km=1),
        Arista(nodo_origen_id=b, nodo_destino_id=d, distancia_km=1),
        Arista(nodo_origen_id=a, nodo_destino_id=c, distancia_km=1),
        Arista(nodo_origen_id=c, nodo_destino_id=d, distancia_km=10),
    ]

    camino, distancia = calcular_ruta_mas_corta(aristas, a, d)

    assert camino == [a, b, d]
    assert distancia == 2


def test_grafo_es_no_dirigido():
    a, b = uuid4(), uuid4()
    aristas = [Arista(nodo_origen_id=a, nodo_destino_id=b, distancia_km=5)]

    camino, distancia = calcular_ruta_mas_corta(aristas, b, a)

    assert camino == [b, a]
    assert distancia == 5


def test_origen_igual_a_destino():
    a = uuid4()

    camino, distancia = calcular_ruta_mas_corta([], a, a)

    assert camino == [a]
    assert distancia == 0


def test_sin_camino_posible_lanza_error():
    a, b, c = uuid4(), uuid4(), uuid4()
    aristas = [Arista(nodo_origen_id=a, nodo_destino_id=b, distancia_km=5)]

    with pytest.raises(SinRutaEnGrafo):
        calcular_ruta_mas_corta(aristas, a, c)
