from uuid import uuid4

import pytest

from app.application.use_cases.vehiculo_use_cases import (
    ActualizarVehiculo,
    CrearVehiculo,
    EliminarVehiculo,
    ObtenerVehiculo,
)
from app.domain.entities import EstadoVehiculo, TipoVehiculo
from app.domain.exceptions import PlacaDuplicada, VehiculoNoEncontrado
from tests.unit.fakes import FakeEventPublisher, FakeVehiculoRepository


@pytest.fixture
def repo():
    return FakeVehiculoRepository()


@pytest.fixture
def publisher():
    return FakeEventPublisher()


async def test_crear_vehiculo_publica_evento(repo, publisher):
    use_case = CrearVehiculo(repo, publisher)

    vehiculo = await use_case.ejecutar("ABC123", TipoVehiculo.CAMION, 1000.0)

    assert vehiculo.placa == "ABC123"
    assert vehiculo.estado == EstadoVehiculo.DISPONIBLE
    assert len(publisher.eventos) == 1
    assert publisher.eventos[0][0] == "vehiculo.creado"


async def test_crear_vehiculo_con_placa_duplicada_falla(repo, publisher):
    use_case = CrearVehiculo(repo, publisher)
    await use_case.ejecutar("ABC123", TipoVehiculo.CAMION, 1000.0)

    with pytest.raises(PlacaDuplicada):
        await use_case.ejecutar("ABC123", TipoVehiculo.FURGON, 500.0)


async def test_obtener_vehiculo_inexistente_falla(repo):
    use_case = ObtenerVehiculo(repo)

    with pytest.raises(VehiculoNoEncontrado):
        await use_case.ejecutar(uuid4())


async def test_actualizar_vehiculo_cambia_estado(repo, publisher):
    creado = await CrearVehiculo(repo, publisher).ejecutar("XYZ999", TipoVehiculo.VAN, 300.0)

    actualizar = ActualizarVehiculo(repo, publisher)
    actualizado = await actualizar.ejecutar(creado.id, estado=EstadoVehiculo.MANTENIMIENTO)

    assert actualizado.estado == EstadoVehiculo.MANTENIMIENTO
    assert len(publisher.eventos) == 2


async def test_eliminar_vehiculo_inexistente_falla(repo):
    with pytest.raises(VehiculoNoEncontrado):
        await EliminarVehiculo(repo).ejecutar(uuid4())
