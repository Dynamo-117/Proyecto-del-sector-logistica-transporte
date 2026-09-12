from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.alerta_use_cases import (
    ListarAlertasActivas,
    MarcarMantenimientoRealizado,
)
from app.application.use_cases.lectura_use_cases import RegistrarLecturaOdometro
from app.application.use_cases.vehiculo_use_cases import SincronizarVehiculoConocido
from app.infrastructure.db.alerta_repository import SqlAlchemyAlertaRepository
from app.infrastructure.db.estado_mantenimiento_repository import (
    SqlAlchemyEstadoMantenimientoRepository,
)
from app.infrastructure.db.lectura_repository import SqlAlchemyLecturaOdometroRepository
from app.infrastructure.db.session import get_db_session
from app.infrastructure.db.vehiculo_repository import SqlAlchemyVehiculoConocidoRepository

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_vehiculo_repo(session: DbSession) -> SqlAlchemyVehiculoConocidoRepository:
    return SqlAlchemyVehiculoConocidoRepository(session)


def get_lectura_repo(session: DbSession) -> SqlAlchemyLecturaOdometroRepository:
    return SqlAlchemyLecturaOdometroRepository(session)


def get_estado_repo(session: DbSession) -> SqlAlchemyEstadoMantenimientoRepository:
    return SqlAlchemyEstadoMantenimientoRepository(session)


def get_alerta_repo(session: DbSession) -> SqlAlchemyAlertaRepository:
    return SqlAlchemyAlertaRepository(session)


VehiculoRepo = Annotated[SqlAlchemyVehiculoConocidoRepository, Depends(get_vehiculo_repo)]
LecturaRepo = Annotated[SqlAlchemyLecturaOdometroRepository, Depends(get_lectura_repo)]
EstadoRepo = Annotated[SqlAlchemyEstadoMantenimientoRepository, Depends(get_estado_repo)]
AlertaRepo = Annotated[SqlAlchemyAlertaRepository, Depends(get_alerta_repo)]


def get_registrar_lectura(
    lectura_repo: LecturaRepo,
    vehiculo_repo: VehiculoRepo,
    estado_repo: EstadoRepo,
    alerta_repo: AlertaRepo,
) -> RegistrarLecturaOdometro:
    return RegistrarLecturaOdometro(lectura_repo, vehiculo_repo, estado_repo, alerta_repo)


def get_listar_alertas_activas(
    alerta_repo: AlertaRepo, vehiculo_repo: VehiculoRepo
) -> ListarAlertasActivas:
    return ListarAlertasActivas(alerta_repo, vehiculo_repo)


def get_marcar_mantenimiento_realizado(
    alerta_repo: AlertaRepo, estado_repo: EstadoRepo, lectura_repo: LecturaRepo
) -> MarcarMantenimientoRealizado:
    return MarcarMantenimientoRealizado(alerta_repo, estado_repo, lectura_repo)


def get_sincronizar_vehiculo(vehiculo_repo: VehiculoRepo) -> SincronizarVehiculoConocido:
    return SincronizarVehiculoConocido(vehiculo_repo)
