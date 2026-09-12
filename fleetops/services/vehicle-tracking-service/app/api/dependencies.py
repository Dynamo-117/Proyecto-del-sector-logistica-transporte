from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.realtime import RealtimeBroadcaster
from app.application.use_cases.telemetria_use_cases import (
    IngestarTelemetria,
    ListarHistoricoTelemetria,
    ObtenerEstadoActual,
)
from app.application.use_cases.vehiculo_use_cases import RegistrarVehiculoConocido
from app.infrastructure.db.session import get_db_session
from app.infrastructure.db.telemetria_repository import SqlAlchemyTelemetriaRepository
from app.infrastructure.db.vehiculo_conocido_repository import SqlAlchemyVehiculoConocidoRepository

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_broadcaster(request: Request) -> RealtimeBroadcaster:
    return request.app.state.broadcaster


Broadcaster = Annotated[RealtimeBroadcaster, Depends(get_broadcaster)]


def get_telemetria_repo(session: DbSession) -> SqlAlchemyTelemetriaRepository:
    return SqlAlchemyTelemetriaRepository(session)


def get_vehiculo_repo(session: DbSession) -> SqlAlchemyVehiculoConocidoRepository:
    return SqlAlchemyVehiculoConocidoRepository(session)


TelemetriaRepo = Annotated[SqlAlchemyTelemetriaRepository, Depends(get_telemetria_repo)]
VehiculoRepo = Annotated[SqlAlchemyVehiculoConocidoRepository, Depends(get_vehiculo_repo)]


def get_ingestar_telemetria(
    telemetria_repo: TelemetriaRepo, vehiculo_repo: VehiculoRepo, broadcaster: Broadcaster
) -> IngestarTelemetria:
    return IngestarTelemetria(telemetria_repo, vehiculo_repo, broadcaster)


def get_obtener_estado_actual(
    telemetria_repo: TelemetriaRepo, vehiculo_repo: VehiculoRepo
) -> ObtenerEstadoActual:
    return ObtenerEstadoActual(telemetria_repo, vehiculo_repo)


def get_listar_historico(
    telemetria_repo: TelemetriaRepo, vehiculo_repo: VehiculoRepo
) -> ListarHistoricoTelemetria:
    return ListarHistoricoTelemetria(telemetria_repo, vehiculo_repo)


def get_registrar_vehiculo(vehiculo_repo: VehiculoRepo) -> RegistrarVehiculoConocido:
    return RegistrarVehiculoConocido(vehiculo_repo)
