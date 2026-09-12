from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.events import EventPublisher
from app.application.ports.repositories import (
    ConductorRepository,
    UsuarioRepository,
    VehiculoRepository,
)
from app.application.use_cases.asignacion_use_cases import (
    AsignarConductorAVehiculo,
    DesasignarConductorDeVehiculo,
)
from app.application.use_cases.auth_use_cases import AutenticarUsuario, ObtenerUsuarioAutenticado
from app.application.use_cases.conductor_use_cases import (
    ActualizarConductor,
    CrearConductor,
    EliminarConductor,
    ListarConductores,
    ObtenerConductor,
)
from app.application.use_cases.vehiculo_use_cases import (
    ActualizarVehiculo,
    CrearVehiculo,
    EliminarVehiculo,
    ListarVehiculos,
    ObtenerVehiculo,
)
from app.core.config import get_settings
from app.infrastructure.db.repositorio_factory import (
    RepositorioFactory,
    SqlAlchemyRepositorioFactory,
)
from app.infrastructure.db.session import get_db_session
from app.infrastructure.security.jwt_token_service import JWTTokenService
from app.infrastructure.security.password_hasher import BcryptPasswordHasher

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_event_publisher(request: Request) -> EventPublisher:
    return request.app.state.event_publisher


Publisher = Annotated[EventPublisher, Depends(get_event_publisher)]


def get_repositorio_factory() -> RepositorioFactory:
    return SqlAlchemyRepositorioFactory()


RepositorioFactoryDep = Annotated[RepositorioFactory, Depends(get_repositorio_factory)]


def get_vehiculo_repo(session: DbSession, factory: RepositorioFactoryDep) -> VehiculoRepository:
    return factory.crear_vehiculo_repo(session)


def get_conductor_repo(session: DbSession, factory: RepositorioFactoryDep) -> ConductorRepository:
    return factory.crear_conductor_repo(session)


VehiculoRepo = Annotated[VehiculoRepository, Depends(get_vehiculo_repo)]
ConductorRepo = Annotated[ConductorRepository, Depends(get_conductor_repo)]


def get_crear_vehiculo(repo: VehiculoRepo, publisher: Publisher) -> CrearVehiculo:
    return CrearVehiculo(repo, publisher)


def get_obtener_vehiculo(repo: VehiculoRepo) -> ObtenerVehiculo:
    return ObtenerVehiculo(repo)


def get_listar_vehiculos(repo: VehiculoRepo) -> ListarVehiculos:
    return ListarVehiculos(repo)


def get_actualizar_vehiculo(repo: VehiculoRepo, publisher: Publisher) -> ActualizarVehiculo:
    return ActualizarVehiculo(repo, publisher)


def get_eliminar_vehiculo(repo: VehiculoRepo) -> EliminarVehiculo:
    return EliminarVehiculo(repo)


def get_crear_conductor(repo: ConductorRepo) -> CrearConductor:
    return CrearConductor(repo)


def get_obtener_conductor(repo: ConductorRepo) -> ObtenerConductor:
    return ObtenerConductor(repo)


def get_listar_conductores(repo: ConductorRepo) -> ListarConductores:
    return ListarConductores(repo)


def get_actualizar_conductor(repo: ConductorRepo) -> ActualizarConductor:
    return ActualizarConductor(repo)


def get_eliminar_conductor(repo: ConductorRepo) -> EliminarConductor:
    return EliminarConductor(repo)


def get_asignar_conductor(
    vehiculo_repo: VehiculoRepo, conductor_repo: ConductorRepo, publisher: Publisher
) -> AsignarConductorAVehiculo:
    return AsignarConductorAVehiculo(vehiculo_repo, conductor_repo, publisher)


def get_desasignar_conductor(
    vehiculo_repo: VehiculoRepo, conductor_repo: ConductorRepo, publisher: Publisher
) -> DesasignarConductorDeVehiculo:
    return DesasignarConductorDeVehiculo(vehiculo_repo, conductor_repo, publisher)


def get_usuario_repo(session: DbSession, factory: RepositorioFactoryDep) -> UsuarioRepository:
    return factory.crear_usuario_repo(session)


UsuarioRepo = Annotated[UsuarioRepository, Depends(get_usuario_repo)]


def get_password_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


PasswordHasherDep = Annotated[BcryptPasswordHasher, Depends(get_password_hasher)]


def get_token_service() -> JWTTokenService:
    settings = get_settings()
    return JWTTokenService(
        settings.jwt_secret_key, settings.jwt_algorithm, settings.jwt_expire_minutos
    )


TokenServiceDep = Annotated[JWTTokenService, Depends(get_token_service)]


def get_autenticar_usuario(
    repo: UsuarioRepo, hasher: PasswordHasherDep, tokens: TokenServiceDep
) -> AutenticarUsuario:
    return AutenticarUsuario(repo, hasher, tokens)


def get_obtener_usuario_autenticado(
    repo: UsuarioRepo, tokens: TokenServiceDep
) -> ObtenerUsuarioAutenticado:
    return ObtenerUsuarioAutenticado(repo, tokens)
