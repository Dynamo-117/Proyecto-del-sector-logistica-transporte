from uuid import uuid4

import pytest

from app.application.use_cases.lectura_use_cases import RegistrarLecturaOdometro
from app.domain.entities import TipoAlerta, VehiculoConocido
from app.domain.exceptions import VehiculoDesconocido
from tests.unit.fakes import (
    FakeAlertaRepository,
    FakeEstadoMantenimientoRepository,
    FakeLecturaOdometroRepository,
    FakeVehiculoConocidoRepository,
)


@pytest.fixture
def repos():
    return {
        "lectura": FakeLecturaOdometroRepository(),
        "vehiculo": FakeVehiculoConocidoRepository(),
        "estado": FakeEstadoMantenimientoRepository(),
        "alerta": FakeAlertaRepository(),
    }


def _use_case(repos) -> RegistrarLecturaOdometro:
    return RegistrarLecturaOdometro(
        repos["lectura"], repos["vehiculo"], repos["estado"], repos["alerta"]
    )


async def test_registrar_lectura_de_vehiculo_desconocido_falla(repos):
    with pytest.raises(VehiculoDesconocido):
        await _use_case(repos).ejecutar(uuid4(), 100, 10)


async def test_registrar_lectura_sin_superar_umbral_no_genera_alertas(repos):
    vehiculo_id = uuid4()
    await repos["vehiculo"].registrar_o_actualizar(VehiculoConocido(id=vehiculo_id, placa="ABC123"))

    lectura, alertas = await _use_case(repos).ejecutar(vehiculo_id, 100, 5)

    assert lectura.kilometraje_km == 100
    assert alertas == []


async def test_registrar_lectura_que_supera_umbral_genera_alerta(repos):
    vehiculo_id = uuid4()
    await repos["vehiculo"].registrar_o_actualizar(VehiculoConocido(id=vehiculo_id, placa="ABC123"))

    _, alertas = await _use_case(repos).ejecutar(vehiculo_id, 10_000, 0)

    assert len(alertas) == 1
    assert alertas[0].tipo == TipoAlerta.CAMBIO_ACEITE


async def test_registrar_lectura_no_duplica_alerta_ya_activa(repos):
    vehiculo_id = uuid4()
    await repos["vehiculo"].registrar_o_actualizar(VehiculoConocido(id=vehiculo_id, placa="ABC123"))
    use_case = _use_case(repos)

    await use_case.ejecutar(vehiculo_id, 10_000, 0)
    _, alertas_segunda_vez = await use_case.ejecutar(vehiculo_id, 10_500, 0)

    assert alertas_segunda_vez == []


async def test_registrar_lectura_puede_generar_ambos_tipos_de_alerta(repos):
    vehiculo_id = uuid4()
    await repos["vehiculo"].registrar_o_actualizar(VehiculoConocido(id=vehiculo_id, placa="ABC123"))

    _, alertas = await _use_case(repos).ejecutar(vehiculo_id, 20_000, 0)

    tipos = {a.tipo for a in alertas}
    assert tipos == {TipoAlerta.CAMBIO_ACEITE, TipoAlerta.REVISION_GENERAL}
