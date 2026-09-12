from uuid import uuid4

import pytest

from app.application.use_cases.auth_use_cases import (
    AutenticarUsuario,
    CrearUsuario,
    ObtenerUsuarioAutenticado,
)
from app.domain.entities import RolUsuario, Usuario
from app.domain.exceptions import (
    CredencialesInvalidas,
    EmailDuplicado,
    UsuarioInactivo,
    UsuarioNoEncontrado,
)
from app.infrastructure.security.jwt_token_service import JWTTokenService
from app.infrastructure.security.password_hasher import BcryptPasswordHasher
from tests.unit.fakes import FakeUsuarioRepository


@pytest.fixture
def repo():
    return FakeUsuarioRepository()


@pytest.fixture
def hasher():
    return BcryptPasswordHasher()


@pytest.fixture
def tokens():
    return JWTTokenService("secreto-de-prueba", "HS256", expire_minutos=60)


async def _crear_usuario(
    repo,
    hasher,
    email="ana@fleetops.com",
    password="clave123",
    rol=RolUsuario.OPERADOR,
    activo=True,
):
    usuario = Usuario(email=email, password_hash=hasher.hashear(password), rol=rol, activo=activo)
    return await repo.crear(usuario)


async def test_crear_usuario(repo, hasher):
    usuario = await CrearUsuario(repo, hasher).ejecutar(
        "admin@fleetops.com", "clave123", RolUsuario.ADMINISTRADOR
    )

    assert usuario.email == "admin@fleetops.com"
    assert usuario.rol == RolUsuario.ADMINISTRADOR
    assert usuario.password_hash != "clave123"


async def test_crear_usuario_con_email_duplicado_falla(repo, hasher):
    use_case = CrearUsuario(repo, hasher)
    await use_case.ejecutar("admin@fleetops.com", "clave123", RolUsuario.ADMINISTRADOR)

    with pytest.raises(EmailDuplicado):
        await use_case.ejecutar("admin@fleetops.com", "otra-clave", RolUsuario.OPERADOR)


async def test_autenticar_usuario_exitoso_devuelve_token(repo, hasher, tokens):
    await _crear_usuario(repo, hasher, email="ana@fleetops.com", password="clave123")

    token = await AutenticarUsuario(repo, hasher, tokens).ejecutar("ana@fleetops.com", "clave123")

    payload = tokens.decodificar_token(token)
    assert payload["rol"] == RolUsuario.OPERADOR.value


async def test_autenticar_usuario_con_password_incorrecta_falla(repo, hasher, tokens):
    await _crear_usuario(repo, hasher, email="ana@fleetops.com", password="clave123")

    with pytest.raises(CredencialesInvalidas):
        await AutenticarUsuario(repo, hasher, tokens).ejecutar("ana@fleetops.com", "incorrecta")


async def test_autenticar_usuario_inexistente_falla(repo, hasher, tokens):
    with pytest.raises(CredencialesInvalidas):
        await AutenticarUsuario(repo, hasher, tokens).ejecutar("nadie@fleetops.com", "clave123")


async def test_autenticar_usuario_inactivo_falla(repo, hasher, tokens):
    await _crear_usuario(
        repo, hasher, email="inactivo@fleetops.com", password="clave123", activo=False
    )

    with pytest.raises(UsuarioInactivo):
        await AutenticarUsuario(repo, hasher, tokens).ejecutar("inactivo@fleetops.com", "clave123")


async def test_obtener_usuario_autenticado_con_token_valido(repo, hasher, tokens):
    usuario = await _crear_usuario(repo, hasher, email="ana@fleetops.com", password="clave123")
    token = tokens.crear_token(str(usuario.id), usuario.rol.value)

    obtenido = await ObtenerUsuarioAutenticado(repo, tokens).ejecutar(token)

    assert obtenido.id == usuario.id
    assert obtenido.email == "ana@fleetops.com"


async def test_obtener_usuario_autenticado_con_token_de_usuario_borrado_falla(repo, hasher, tokens):
    token = tokens.crear_token(str(uuid4()), RolUsuario.OPERADOR.value)

    with pytest.raises(UsuarioNoEncontrado):
        await ObtenerUsuarioAutenticado(repo, tokens).ejecutar(token)
