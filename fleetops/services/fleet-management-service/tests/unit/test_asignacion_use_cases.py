from uuid import uuid4

import pytest

from app.application.use_cases.asignacion_use_cases import (
    AsignarConductorAVehiculo,
    DesasignarConductorDeVehiculo,
)
from app.domain.entities import Conductor, EstadoConductor, EstadoVehiculo, TipoVehiculo, Vehiculo
from app.domain.exceptions import (
    ConductorNoDisponible,
    ConductorNoEncontrado,
    VehiculoNoDisponible,
    VehiculoNoEncontrado,
)
from tests.unit.fakes import FakeConductorRepository, FakeEventPublisher, FakeVehiculoRepository


@pytest.fixture
async def vehiculo_repo():
    repo = FakeVehiculoRepository()
    return repo


@pytest.fixture
async def conductor_repo():
    return FakeConductorRepository()


@pytest.fixture
def publisher():
    return FakeEventPublisher()


async def test_asignar_conductor_a_vehiculo_disponibles(vehiculo_repo, conductor_repo, publisher):
    vehiculo = Vehiculo(placa="AAA111", tipo=TipoVehiculo.CAMION, capacidad_kg=1000)
    conductor = Conductor(nombre="Ana", licencia="LIC-100")
    await vehiculo_repo.crear(vehiculo)
    await conductor_repo.crear(conductor)

    use_case = AsignarConductorAVehiculo(vehiculo_repo, conductor_repo, publisher)
    resultado = await use_case.ejecutar(vehiculo.id, conductor.id)

    assert resultado.conductor_id == conductor.id
    assert resultado.estado == EstadoVehiculo.EN_RUTA
    conductor_actualizado = await conductor_repo.obtener_por_id(conductor.id)
    assert conductor_actualizado.estado == EstadoConductor.ASIGNADO
    assert publisher.eventos[-1][0] == "vehiculo.conductor_asignado"


async def test_asignar_es_idempotente_si_ya_esta_asignado(vehiculo_repo, conductor_repo, publisher):
    vehiculo = Vehiculo(placa="AAA111", tipo=TipoVehiculo.CAMION, capacidad_kg=1000)
    conductor = Conductor(nombre="Ana", licencia="LIC-100")
    await vehiculo_repo.crear(vehiculo)
    await conductor_repo.crear(conductor)

    use_case = AsignarConductorAVehiculo(vehiculo_repo, conductor_repo, publisher)
    await use_case.ejecutar(vehiculo.id, conductor.id)
    resultado = await use_case.ejecutar(vehiculo.id, conductor.id)

    assert resultado.conductor_id == conductor.id
    assert len(publisher.eventos) == 1


async def test_asignar_vehiculo_ya_ocupado_falla(vehiculo_repo, conductor_repo, publisher):
    vehiculo = Vehiculo(placa="AAA111", tipo=TipoVehiculo.CAMION, capacidad_kg=1000)
    conductor1 = Conductor(nombre="Ana", licencia="LIC-100")
    conductor2 = Conductor(nombre="Beto", licencia="LIC-200")
    await vehiculo_repo.crear(vehiculo)
    await conductor_repo.crear(conductor1)
    await conductor_repo.crear(conductor2)

    use_case = AsignarConductorAVehiculo(vehiculo_repo, conductor_repo, publisher)
    await use_case.ejecutar(vehiculo.id, conductor1.id)

    with pytest.raises(VehiculoNoDisponible):
        await use_case.ejecutar(vehiculo.id, conductor2.id)


async def test_asignar_conductor_ya_asignado_a_otro_vehiculo_falla(
    vehiculo_repo, conductor_repo, publisher
):
    vehiculo1 = Vehiculo(placa="AAA111", tipo=TipoVehiculo.CAMION, capacidad_kg=1000)
    vehiculo2 = Vehiculo(placa="BBB222", tipo=TipoVehiculo.FURGON, capacidad_kg=500)
    conductor = Conductor(nombre="Ana", licencia="LIC-100")
    await vehiculo_repo.crear(vehiculo1)
    await vehiculo_repo.crear(vehiculo2)
    await conductor_repo.crear(conductor)

    use_case = AsignarConductorAVehiculo(vehiculo_repo, conductor_repo, publisher)
    await use_case.ejecutar(vehiculo1.id, conductor.id)

    with pytest.raises(ConductorNoDisponible):
        await use_case.ejecutar(vehiculo2.id, conductor.id)


async def test_asignar_vehiculo_inexistente_falla(vehiculo_repo, conductor_repo, publisher):
    with pytest.raises(VehiculoNoEncontrado):
        await AsignarConductorAVehiculo(vehiculo_repo, conductor_repo, publisher).ejecutar(
            uuid4(), uuid4()
        )


async def test_asignar_conductor_inexistente_falla(vehiculo_repo, conductor_repo, publisher):
    vehiculo = Vehiculo(placa="AAA111", tipo=TipoVehiculo.CAMION, capacidad_kg=1000)
    await vehiculo_repo.crear(vehiculo)

    with pytest.raises(ConductorNoEncontrado):
        await AsignarConductorAVehiculo(vehiculo_repo, conductor_repo, publisher).ejecutar(
            vehiculo.id, uuid4()
        )


async def test_desasignar_conductor_libera_ambos(vehiculo_repo, conductor_repo, publisher):
    vehiculo = Vehiculo(placa="AAA111", tipo=TipoVehiculo.CAMION, capacidad_kg=1000)
    conductor = Conductor(nombre="Ana", licencia="LIC-100")
    await vehiculo_repo.crear(vehiculo)
    await conductor_repo.crear(conductor)

    asignar = AsignarConductorAVehiculo(vehiculo_repo, conductor_repo, publisher)
    await asignar.ejecutar(vehiculo.id, conductor.id)

    desasignar = DesasignarConductorDeVehiculo(vehiculo_repo, conductor_repo, publisher)
    resultado = await desasignar.ejecutar(vehiculo.id)

    assert resultado.conductor_id is None
    assert resultado.estado == EstadoVehiculo.DISPONIBLE
    conductor_actualizado = await conductor_repo.obtener_por_id(conductor.id)
    assert conductor_actualizado.estado == EstadoConductor.DISPONIBLE
