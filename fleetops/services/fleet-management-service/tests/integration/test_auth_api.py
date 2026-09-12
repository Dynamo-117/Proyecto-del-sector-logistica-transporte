import pytest_asyncio

from app.domain.entities import RolUsuario, Usuario
from app.infrastructure.db.usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.security.password_hasher import BcryptPasswordHasher


@pytest_asyncio.fixture
async def usuario_operador(session_factory):
    async with session_factory() as session:
        repo = SqlAlchemyUsuarioRepository(session)
        hasher = BcryptPasswordHasher()
        usuario = Usuario(
            email="operador@fleetops.com",
            password_hash=hasher.hashear("clave123"),
            rol=RolUsuario.OPERADOR,
        )
        return await repo.crear(usuario)


async def test_login_exitoso_devuelve_token(client, usuario_operador):
    respuesta = await client.post(
        "/auth/login", json={"email": "operador@fleetops.com", "password": "clave123"}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["access_token"]


async def test_login_con_password_incorrecta_devuelve_401(client, usuario_operador):
    respuesta = await client.post(
        "/auth/login", json={"email": "operador@fleetops.com", "password": "incorrecta"}
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "CREDENCIALES_INVALIDAS"


async def test_login_con_email_inexistente_devuelve_401(client):
    respuesta = await client.post(
        "/auth/login", json={"email": "nadie@fleetops.com", "password": "clave123"}
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "CREDENCIALES_INVALIDAS"


async def test_me_con_token_valido_devuelve_usuario(client, usuario_operador):
    login = await client.post(
        "/auth/login", json={"email": "operador@fleetops.com", "password": "clave123"}
    )
    token = login.json()["access_token"]

    respuesta = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["email"] == "operador@fleetops.com"
    assert cuerpo["rol"] == "OPERADOR"


async def test_me_sin_token_devuelve_401(client):
    respuesta = await client.get("/auth/me")

    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "TOKEN_INVALIDO"


async def test_me_con_token_invalido_devuelve_401(client):
    respuesta = await client.get("/auth/me", headers={"Authorization": "Bearer token-basura"})

    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "TOKEN_INVALIDO"
