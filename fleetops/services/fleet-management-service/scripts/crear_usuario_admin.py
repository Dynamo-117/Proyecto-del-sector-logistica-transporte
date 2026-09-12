"""Crea el primer usuario ADMINISTRADOR, conectandose directamente a la base
de datos configurada en DATABASE_URL (.env). No hardcodea credenciales: el
email se pasa por argumento y la contrasena se pide de forma interactiva
(o se pasa por --password, util solo para scripts de CI/seed automatizado).

Uso (desde la raiz del servicio, para que el paquete "app" sea importable):
    python -m scripts.crear_usuario_admin --email admin@fleetops.com
"""

import argparse
import asyncio
import getpass

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.application.use_cases.auth_use_cases import CrearUsuario
from app.core.config import get_settings
from app.domain.entities import RolUsuario
from app.domain.exceptions import EmailDuplicado
from app.infrastructure.db.usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.security.password_hasher import BcryptPasswordHasher


async def crear_admin(email: str, password: str) -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        repo = SqlAlchemyUsuarioRepository(session)
        use_case = CrearUsuario(repo, BcryptPasswordHasher())
        try:
            usuario = await use_case.ejecutar(email, password, RolUsuario.ADMINISTRADOR)
        except EmailDuplicado:
            print(f"Ya existe un usuario con el email '{email}'")
            await engine.dispose()
            return

    print(f"Usuario ADMINISTRADOR creado: {usuario.email} (id={usuario.id})")
    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument(
        "--password", default=None, help="Si se omite, se pide de forma interactiva (recomendado)"
    )
    args = parser.parse_args()

    password = args.password or getpass.getpass("Contrasena: ")
    asyncio.run(crear_admin(args.email, password))


if __name__ == "__main__":
    main()
