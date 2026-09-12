from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.application.use_cases.telemetria_use_cases import (
    IngestarTelemetria,
    ListarHistoricoTelemetria,
    ObtenerEstadoActual,
)
from app.domain.entities import EstadoMovimiento, VehiculoConocido
from app.domain.exceptions import TelemetriaInvalida, TelemetriaNoDisponible, VehiculoDesconocido
from tests.unit.fakes import (
    FakeBroadcaster,
    FakeTelemetriaRepository,
    FakeVehiculoConocidoRepository,
)


@pytest.fixture
def vehiculo_repo():
    return FakeVehiculoConocidoRepository()


@pytest.fixture
def telemetria_repo():
    return FakeTelemetriaRepository()


@pytest.fixture
def broadcaster():
    return FakeBroadcaster()


async def test_ingestar_telemetria_de_vehiculo_desconocido_falla(
    vehiculo_repo, telemetria_repo, broadcaster
):
    use_case = IngestarTelemetria(telemetria_repo, vehiculo_repo, broadcaster)

    with pytest.raises(VehiculoDesconocido):
        await use_case.ejecutar(uuid4(), 4.71, -74.07, 30.0)


async def test_ingestar_telemetria_publica_evento_en_tiempo_real(
    vehiculo_repo, telemetria_repo, broadcaster
):
    vehiculo_id = uuid4()
    await vehiculo_repo.registrar(VehiculoConocido(id=vehiculo_id, placa="ABC123"))

    use_case = IngestarTelemetria(telemetria_repo, vehiculo_repo, broadcaster)
    telemetria = await use_case.ejecutar(vehiculo_id, 4.71, -74.07, 45.0)

    assert telemetria.estado_movimiento == EstadoMovimiento.EN_MOVIMIENTO
    assert len(broadcaster.publicados) == 1
    assert broadcaster.publicados[0][0] == vehiculo_id


async def test_ingestar_telemetria_con_latitud_invalida_falla(
    vehiculo_repo, telemetria_repo, broadcaster
):
    vehiculo_id = uuid4()
    await vehiculo_repo.registrar(VehiculoConocido(id=vehiculo_id, placa="ABC123"))
    use_case = IngestarTelemetria(telemetria_repo, vehiculo_repo, broadcaster)

    with pytest.raises(TelemetriaInvalida):
        await use_case.ejecutar(vehiculo_id, 999.0, -74.07, 10.0)


async def test_obtener_estado_actual_sin_telemetria_falla(vehiculo_repo, telemetria_repo):
    vehiculo_id = uuid4()
    await vehiculo_repo.registrar(VehiculoConocido(id=vehiculo_id, placa="ABC123"))
    use_case = ObtenerEstadoActual(telemetria_repo, vehiculo_repo)

    with pytest.raises(TelemetriaNoDisponible):
        await use_case.ejecutar(vehiculo_id)


async def test_obtener_estado_actual_devuelve_lo_mas_reciente(
    vehiculo_repo, telemetria_repo, broadcaster
):
    vehiculo_id = uuid4()
    await vehiculo_repo.registrar(VehiculoConocido(id=vehiculo_id, placa="ABC123"))
    ingestar = IngestarTelemetria(telemetria_repo, vehiculo_repo, broadcaster)
    ahora = datetime.now(UTC)
    await ingestar.ejecutar(vehiculo_id, 4.71, -74.07, 10.0, timestamp=ahora)
    ultima = await ingestar.ejecutar(
        vehiculo_id, 4.72, -74.08, 0.0, timestamp=ahora + timedelta(seconds=1)
    )

    estado = await ObtenerEstadoActual(telemetria_repo, vehiculo_repo).ejecutar(vehiculo_id)

    assert estado.timestamp == ultima.timestamp
    assert estado.estado_movimiento == EstadoMovimiento.DETENIDO


async def test_listar_historico_de_vehiculo_desconocido_falla(vehiculo_repo, telemetria_repo):
    with pytest.raises(VehiculoDesconocido):
        await ListarHistoricoTelemetria(telemetria_repo, vehiculo_repo).ejecutar(uuid4())


async def test_listar_historico_devuelve_registros(vehiculo_repo, telemetria_repo, broadcaster):
    vehiculo_id = uuid4()
    await vehiculo_repo.registrar(VehiculoConocido(id=vehiculo_id, placa="ABC123"))
    ingestar = IngestarTelemetria(telemetria_repo, vehiculo_repo, broadcaster)
    await ingestar.ejecutar(vehiculo_id, 4.71, -74.07, 10.0)
    await ingestar.ejecutar(vehiculo_id, 4.72, -74.08, 20.0)

    historico = await ListarHistoricoTelemetria(telemetria_repo, vehiculo_repo).ejecutar(
        vehiculo_id
    )

    assert len(historico) == 2
