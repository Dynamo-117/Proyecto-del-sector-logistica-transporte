"""Crea los dos usuarios de demostracion (un ADMINISTRADOR y un OPERADOR) para
poder probar todo el sistema tras una instalacion limpia. Es idempotente: si
un usuario ya existe, lo informa y continua con el siguiente.

Uso (desde la raiz del servicio, con el entorno virtual activo):
    python -m scripts.crear_usuarios_demo

Credenciales creadas (solo para demostracion/evaluacion, no para produccion):
    admin@fleetops.com     / Admin123!      (ADMINISTRADOR)
    operador@fleetops.com  / Operador123!   (OPERADOR)
"""

import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.application.use_cases.auth_use_cases import CrearUsuario
from app.core.config import get_settings
from app.domain.entities import RolUsuario
from app.domain.exceptions import EmailDuplicado
from app.infrastructure.db.usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.security.password_hasher import BcryptPasswordHasher

USUARIOS_DEMO = [
    ("admin@fleetops.com", "Admin123!", RolUsuario.ADMINISTRADOR),
    ("operador@fleetops.com", "Operador123!", RolUsuario.OPERADOR),
]


async def crear_usuarios_demo() -> None:
    engine = create_async_engine(get_settings().database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    for email, password, rol in USUARIOS_DEMO:
        async with session_factory() as session:
            use_case = CrearUsuario(SqlAlchemyUsuarioRepository(session), BcryptPasswordHasher())
            try:
                usuario = await use_case.ejecutar(email, password, rol)
            except EmailDuplicado:
                print(f"Ya existe: {email} ({rol.value})")
                continue
        print(f"Creado: {usuario.email} ({rol.value}) id={usuario.id}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(crear_usuarios_demo())
