from uuid import uuid4

from app.application.use_cases.vehiculo_use_cases import (
    ActualizarEstadoVehiculoPorAsignacionConductor,
    SincronizarVehiculoDisponible,
)
from app.domain.entities import EstadoVehiculo, VehiculoDisponible
from tests.unit.fakes import FakeVehiculoDisponibleRepository


async def test_sincronizar_vehiculo_disponible_registra_datos_completos():
    repo = FakeVehiculoDisponibleRepository()
    vehiculo_id = uuid4()

    vehiculo = await SincronizarVehiculoDisponible(repo).ejecutar(
        vehiculo_id, "ABC123", 1000, "DISPONIBLE"
    )

    assert vehiculo.placa == "ABC123"
    assert vehiculo.capacidad_kg == 1000
    assert vehiculo.estado == EstadoVehiculo.DISPONIBLE


async def test_actualizar_estado_por_conductor_asignado():
    repo = FakeVehiculoDisponibleRepository()
    vehiculo_id = uuid4()
    await repo.registrar_o_actualizar(
        VehiculoDisponible(
            id=vehiculo_id, placa="ABC123", capacidad_kg=1000, estado=EstadoVehiculo.DISPONIBLE
        )
    )

    await ActualizarEstadoVehiculoPorAsignacionConductor(repo).ejecutar(
        vehiculo_id, EstadoVehiculo.EN_RUTA
    )

    actualizado = await repo.obtener(vehiculo_id)
    assert actualizado.estado == EstadoVehiculo.EN_RUTA


async def test_actualizar_estado_de_vehiculo_desconocido_no_falla():
    repo = FakeVehiculoDisponibleRepository()

    await ActualizarEstadoVehiculoPorAsignacionConductor(repo).ejecutar(
        uuid4(), EstadoVehiculo.EN_RUTA
    )
