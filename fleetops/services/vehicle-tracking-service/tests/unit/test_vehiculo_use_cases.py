from uuid import uuid4

from app.application.use_cases.vehiculo_use_cases import RegistrarVehiculoConocido
from tests.unit.fakes import FakeVehiculoConocidoRepository


async def test_registrar_vehiculo_conocido():
    repo = FakeVehiculoConocidoRepository()
    vehiculo_id = uuid4()

    vehiculo = await RegistrarVehiculoConocido(repo).ejecutar(vehiculo_id, "ABC123")

    assert vehiculo.id == vehiculo_id
    assert vehiculo.placa == "ABC123"
    assert await repo.existe(vehiculo_id)


async def test_registrar_vehiculo_conocido_es_idempotente():
    repo = FakeVehiculoConocidoRepository()
    vehiculo_id = uuid4()
    use_case = RegistrarVehiculoConocido(repo)

    primero = await use_case.ejecutar(vehiculo_id, "ABC123")
    segundo = await use_case.ejecutar(vehiculo_id, "ABC123")

    assert primero.registrado_en == segundo.registrado_en
