from uuid import uuid4

import pytest

from app.application.use_cases.plan_use_cases import PlanificarRutaConParadas
from app.domain.entities import Arista, Nodo
from app.domain.exceptions import NodoNoEncontrado, PlanInvalido, SinRutaEnGrafo
from app.domain.itinerario import ComponenteRuta, Tramo, Trayecto, construir_trayecto
from tests.unit.fakes import FakeAristaRepository, FakeNodoRepository

A, B, C, D = uuid4(), uuid4(), uuid4(), uuid4()


def test_el_componente_abstracto_no_se_puede_instanciar():
    with pytest.raises(TypeError):
        ComponenteRuta()


def test_una_hoja_responde_por_si_sola():
    tramo = Tramo(A, B, 10)

    assert tramo.distancia_km() == 10
    assert tramo.nodos() == [A, B]
    assert tramo.cantidad_tramos() == 1


def test_un_compuesto_suma_a_sus_hijos():
    trayecto = Trayecto("A -> C")
    trayecto.agregar(Tramo(A, B, 10))
    trayecto.agregar(Tramo(B, C, 5))

    assert trayecto.distancia_km() == 15
    assert trayecto.cantidad_tramos() == 2
    assert trayecto.nodos() == [A, B, C]


def test_hojas_y_compuestos_se_tratan_igual_y_se_anidan():
    primero = Trayecto("A -> B")
    primero.agregar(Tramo(A, B, 10))
    segundo = Trayecto("B -> D")
    segundo.agregar(Tramo(B, C, 5))
    segundo.agregar(Tramo(C, D, 7))
    itinerario = Trayecto("Itinerario")
    itinerario.agregar(primero)
    itinerario.agregar(segundo)

    for componente in (Tramo(A, B, 1), primero, itinerario):
        assert isinstance(componente, ComponenteRuta)
        assert componente.distancia_km() > 0

    assert itinerario.distancia_km() == 22
    assert itinerario.cantidad_tramos() == 3
    assert itinerario.nodos() == [A, B, C, D]


def test_describir_devuelve_el_arbol_completo():
    trayecto = Trayecto("A -> B")
    trayecto.agregar(Tramo(A, B, 10))
    itinerario = Trayecto("Itinerario")
    itinerario.agregar(trayecto)

    arbol = itinerario.describir({A: "Alfa", B: "Beta"})

    assert arbol["tipo"] == "trayecto"
    assert arbol["distancia_km"] == 10
    assert arbol["hijos"][0]["hijos"][0] == {
        "tipo": "tramo",
        "nombre": "Alfa -> Beta",
        "distancia_km": 10,
        "cantidad_tramos": 1,
        "hijos": [],
    }


def test_quitar_un_hijo_actualiza_los_totales():
    trayecto = Trayecto("T")
    tramo = Tramo(A, B, 10)
    trayecto.agregar(tramo)
    trayecto.agregar(Tramo(B, C, 5))

    trayecto.quitar(tramo)

    assert trayecto.distancia_km() == 5
    assert len(trayecto.hijos) == 1


def test_un_trayecto_no_puede_contenerse_a_si_mismo():
    trayecto = Trayecto("T")

    with pytest.raises(ValueError):
        trayecto.agregar(trayecto)


def test_construir_trayecto_usa_la_arista_mas_corta_de_cada_par():
    aristas = [
        Arista(nodo_origen_id=A, nodo_destino_id=B, distancia_km=10),
        Arista(nodo_origen_id=B, nodo_destino_id=A, distancia_km=4),
        Arista(nodo_origen_id=B, nodo_destino_id=C, distancia_km=6),
    ]

    trayecto = construir_trayecto("A -> C", [A, B, C], aristas)

    assert trayecto.distancia_km() == 10
    assert trayecto.cantidad_tramos() == 2


async def _caso(*aristas: tuple):
    nodos, repo_aristas = FakeNodoRepository(), FakeAristaRepository()
    for id_, nombre in ((A, "A"), (B, "B"), (C, "C"), (D, "D")):
        await nodos.crear(Nodo(id=id_, nombre=nombre, latitud=0, longitud=0))
    for origen, destino, km in aristas:
        await repo_aristas.crear(
            Arista(nodo_origen_id=origen, nodo_destino_id=destino, distancia_km=km)
        )
    return PlanificarRutaConParadas(nodos, repo_aristas)


async def test_plan_con_paradas_arma_el_arbol_itinerario_trayectos_tramos():
    caso = await _caso((A, B, 10), (B, C, 5), (C, D, 7))

    itinerario, nombres = await caso.ejecutar([A, C, D])

    assert nombres[C] == "C"
    assert itinerario.distancia_km() == 22
    assert itinerario.cantidad_tramos() == 3
    assert itinerario.nodos() == [A, B, C, D]
    assert [h.nombre for h in itinerario.hijos] == ["A -> C", "C -> D"]


async def test_plan_exige_al_menos_dos_paradas():
    caso = await _caso((A, B, 10))

    with pytest.raises(PlanInvalido):
        await caso.ejecutar([A])


async def test_plan_rechaza_paradas_consecutivas_repetidas():
    caso = await _caso((A, B, 10))

    with pytest.raises(PlanInvalido):
        await caso.ejecutar([A, A])


async def test_plan_con_nodo_inexistente():
    caso = await _caso((A, B, 10))

    with pytest.raises(NodoNoEncontrado):
        await caso.ejecutar([A, uuid4()])


async def test_plan_sin_camino_entre_paradas():
    caso = await _caso((A, B, 10))

    with pytest.raises(SinRutaEnGrafo):
        await caso.ejecutar([A, D])
