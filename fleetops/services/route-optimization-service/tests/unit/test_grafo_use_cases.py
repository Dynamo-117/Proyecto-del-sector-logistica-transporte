from uuid import uuid4

import pytest

from app.application.use_cases.grafo_use_cases import CrearConexion, CrearNodo, ListarNodos
from app.domain.exceptions import NodoNoEncontrado
from tests.unit.fakes import FakeAristaRepository, FakeNodoRepository


@pytest.fixture
def nodo_repo():
    return FakeNodoRepository()


@pytest.fixture
def arista_repo():
    return FakeAristaRepository()


async def test_crear_nodo(nodo_repo):
    nodo = await CrearNodo(nodo_repo).ejecutar("Bogota", 4.71, -74.07)

    assert nodo.nombre == "Bogota"


async def test_listar_nodos(nodo_repo):
    await CrearNodo(nodo_repo).ejecutar("Bogota", 4.71, -74.07)
    await CrearNodo(nodo_repo).ejecutar("Medellin", 6.25, -75.56)

    nodos = await ListarNodos(nodo_repo).ejecutar()

    assert len(nodos) == 2


async def test_crear_conexion_con_nodo_origen_desconocido_falla(nodo_repo, arista_repo):
    destino = await CrearNodo(nodo_repo).ejecutar("Medellin", 6.25, -75.56)

    with pytest.raises(NodoNoEncontrado):
        await CrearConexion(nodo_repo, arista_repo).ejecutar(uuid4(), destino.id, 10)


async def test_crear_conexion_con_nodo_destino_desconocido_falla(nodo_repo, arista_repo):
    origen = await CrearNodo(nodo_repo).ejecutar("Bogota", 4.71, -74.07)

    with pytest.raises(NodoNoEncontrado):
        await CrearConexion(nodo_repo, arista_repo).ejecutar(origen.id, uuid4(), 10)


async def test_crear_conexion_valida(nodo_repo, arista_repo):
    origen = await CrearNodo(nodo_repo).ejecutar("Bogota", 4.71, -74.07)
    destino = await CrearNodo(nodo_repo).ejecutar("Medellin", 6.25, -75.56)

    arista = await CrearConexion(nodo_repo, arista_repo).ejecutar(origen.id, destino.id, 415)

    assert arista.distancia_km == 415
    assert len(await arista_repo.listar_todas()) == 1
