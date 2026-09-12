from uuid import uuid4

import pytest

from app.application.use_cases.conductor_use_cases import (
    ActualizarConductor,
    CrearConductor,
    EliminarConductor,
    ObtenerConductor,
)
from app.domain.entities import EstadoConductor
from app.domain.exceptions import ConductorNoEncontrado, LicenciaDuplicada
from tests.unit.fakes import FakeConductorRepository


@pytest.fixture
def repo():
    return FakeConductorRepository()


async def test_crear_conductor(repo):
    conductor = await CrearConductor(repo).ejecutar("Juan Perez", "LIC-001")

    assert conductor.nombre == "Juan Perez"
    assert conductor.estado == EstadoConductor.DISPONIBLE


async def test_crear_conductor_con_licencia_duplicada_falla(repo):
    use_case = CrearConductor(repo)
    await use_case.ejecutar("Juan Perez", "LIC-001")

    with pytest.raises(LicenciaDuplicada):
        await use_case.ejecutar("Otro Nombre", "LIC-001")


async def test_obtener_conductor_inexistente_falla(repo):
    with pytest.raises(ConductorNoEncontrado):
        await ObtenerConductor(repo).ejecutar(uuid4())


async def test_actualizar_conductor(repo):
    creado = await CrearConductor(repo).ejecutar("Juan Perez", "LIC-002")

    actualizado = await ActualizarConductor(repo).ejecutar(creado.id, nombre="Juan P. Actualizado")

    assert actualizado.nombre == "Juan P. Actualizado"


async def test_eliminar_conductor_inexistente_falla(repo):
    with pytest.raises(ConductorNoEncontrado):
        await EliminarConductor(repo).ejecutar(uuid4())
