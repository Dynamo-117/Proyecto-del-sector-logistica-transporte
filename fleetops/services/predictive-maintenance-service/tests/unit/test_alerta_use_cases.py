from uuid import uuid4

import pytest

from app.application.use_cases.alerta_use_cases import (
    ListarAlertasActivas,
    MarcarMantenimientoRealizado,
)
from app.domain.entities import Alerta, EstadoAlerta, LecturaOdometro, TipoAlerta, VehiculoConocido
from app.domain.exceptions import AlertaNoEncontrada, AlertaYaResuelta, VehiculoDesconocido
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


async def test_listar_alertas_de_vehiculo_desconocido_falla(repos):
    with pytest.raises(VehiculoDesconocido):
        await ListarAlertasActivas(repos["alerta"], repos["vehiculo"]).ejecutar(uuid4())


async def test_listar_alertas_activas(repos):
    vehiculo_id = uuid4()
    await repos["vehiculo"].registrar_o_actualizar(VehiculoConocido(id=vehiculo_id, placa="ABC123"))
    await repos["alerta"].crear(
        Alerta(
            vehiculo_id=vehiculo_id,
            tipo=TipoAlerta.CAMBIO_ACEITE,
            kilometraje_km=10_000,
            horas_motor=0,
        )
    )

    alertas = await ListarAlertasActivas(repos["alerta"], repos["vehiculo"]).ejecutar(vehiculo_id)

    assert len(alertas) == 1


async def test_marcar_alerta_inexistente_falla(repos):
    use_case = MarcarMantenimientoRealizado(repos["alerta"], repos["estado"], repos["lectura"])

    with pytest.raises(AlertaNoEncontrada):
        await use_case.ejecutar(uuid4())


async def test_marcar_alerta_ya_resuelta_falla(repos):
    vehiculo_id = uuid4()
    alerta = await repos["alerta"].crear(
        Alerta(
            vehiculo_id=vehiculo_id,
            tipo=TipoAlerta.CAMBIO_ACEITE,
            kilometraje_km=10_000,
            horas_motor=0,
            estado=EstadoAlerta.RESUELTA,
        )
    )
    use_case = MarcarMantenimientoRealizado(repos["alerta"], repos["estado"], repos["lectura"])

    with pytest.raises(AlertaYaResuelta):
        await use_case.ejecutar(alerta.id)


async def test_marcar_alerta_resuelta_reinicia_la_base_de_desgaste(repos):
    vehiculo_id = uuid4()
    await repos["lectura"].guardar(
        LecturaOdometro(vehiculo_id=vehiculo_id, kilometraje_km=10_200, horas_motor=305)
    )
    alerta = await repos["alerta"].crear(
        Alerta(
            vehiculo_id=vehiculo_id,
            tipo=TipoAlerta.CAMBIO_ACEITE,
            kilometraje_km=10_200,
            horas_motor=305,
        )
    )

    use_case = MarcarMantenimientoRealizado(repos["alerta"], repos["estado"], repos["lectura"])
    resuelta = await use_case.ejecutar(alerta.id)

    assert resuelta.estado == EstadoAlerta.RESUELTA
    assert resuelta.resuelta_en is not None

    estados = await repos["estado"].obtener_todos(vehiculo_id)
    assert estados[TipoAlerta.CAMBIO_ACEITE].km_base == 10_200
    assert estados[TipoAlerta.CAMBIO_ACEITE].horas_base == 305
