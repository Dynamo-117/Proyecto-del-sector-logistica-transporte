from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.asignacion_use_cases import (
    ListarRutasActivas,
    ObtenerRuta,
    SolicitarAsignacionCarga,
)
from app.application.use_cases.grafo_use_cases import CrearConexion, CrearNodo, ListarNodos
from app.application.use_cases.vehiculo_use_cases import (
    ActualizarEstadoVehiculoPorAsignacionConductor,
    SincronizarVehiculoDisponible,
)
from app.infrastructure.db.arista_repository import (
    AristaRepositorioCreador,
    SqlAlchemyAristaRepository,
)
from app.infrastructure.db.carga_repository import (
    CargaRepositorioCreador,
    SqlAlchemyCargaRepository,
)
from app.infrastructure.db.nodo_repository import NodoRepositorioCreador, SqlAlchemyNodoRepository
from app.infrastructure.db.ruta_repository import RutaRepositorioCreador, SqlAlchemyRutaRepository
from app.infrastructure.db.session import get_db_session
from app.infrastructure.db.vehiculo_disponible_repository import (
    SqlAlchemyVehiculoDisponibleRepository,
    VehiculoDisponibleRepositorioCreador,
)

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_nodo_repo(session: DbSession) -> SqlAlchemyNodoRepository:
    return NodoRepositorioCreador().obtener_repositorio(session)


def get_arista_repo(session: DbSession) -> SqlAlchemyAristaRepository:
    return AristaRepositorioCreador().obtener_repositorio(session)


def get_carga_repo(session: DbSession) -> SqlAlchemyCargaRepository:
    return CargaRepositorioCreador().obtener_repositorio(session)


def get_ruta_repo(session: DbSession) -> SqlAlchemyRutaRepository:
    return RutaRepositorioCreador().obtener_repositorio(session)


def get_vehiculo_repo(session: DbSession) -> SqlAlchemyVehiculoDisponibleRepository:
    return VehiculoDisponibleRepositorioCreador().obtener_repositorio(session)


NodoRepo = Annotated[SqlAlchemyNodoRepository, Depends(get_nodo_repo)]
AristaRepo = Annotated[SqlAlchemyAristaRepository, Depends(get_arista_repo)]
CargaRepo = Annotated[SqlAlchemyCargaRepository, Depends(get_carga_repo)]
RutaRepo = Annotated[SqlAlchemyRutaRepository, Depends(get_ruta_repo)]
VehiculoRepo = Annotated[SqlAlchemyVehiculoDisponibleRepository, Depends(get_vehiculo_repo)]


def get_crear_nodo(repo: NodoRepo) -> CrearNodo:
    return CrearNodo(repo)


def get_listar_nodos(repo: NodoRepo) -> ListarNodos:
    return ListarNodos(repo)


def get_crear_conexion(nodo_repo: NodoRepo, arista_repo: AristaRepo) -> CrearConexion:
    return CrearConexion(nodo_repo, arista_repo)


def get_solicitar_asignacion(
    nodo_repo: NodoRepo,
    arista_repo: AristaRepo,
    carga_repo: CargaRepo,
    ruta_repo: RutaRepo,
    vehiculo_repo: VehiculoRepo,
) -> SolicitarAsignacionCarga:
    return SolicitarAsignacionCarga(nodo_repo, arista_repo, carga_repo, ruta_repo, vehiculo_repo)


def get_obtener_ruta(repo: RutaRepo) -> ObtenerRuta:
    return ObtenerRuta(repo)


def get_listar_rutas_activas(repo: RutaRepo) -> ListarRutasActivas:
    return ListarRutasActivas(repo)


def get_sincronizar_vehiculo(repo: VehiculoRepo) -> SincronizarVehiculoDisponible:
    return SincronizarVehiculoDisponible(repo)


def get_actualizar_estado_por_conductor(
    repo: VehiculoRepo,
) -> ActualizarEstadoVehiculoPorAsignacionConductor:
    return ActualizarEstadoVehiculoPorAsignacionConductor(repo)
