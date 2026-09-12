from __future__ import annotations

from uuid import UUID

from app.application.ports.repositories import UsuarioRepository
from app.application.ports.security import PasswordHasher, TokenService
from app.domain.entities import RolUsuario, Usuario
from app.domain.exceptions import (
    CredencialesInvalidas,
    EmailDuplicado,
    UsuarioInactivo,
    UsuarioNoEncontrado,
)


class AutenticarUsuario:
    def __init__(self, repo: UsuarioRepository, hasher: PasswordHasher, tokens: TokenService):
        self._repo = repo
        self._hasher = hasher
        self._tokens = tokens

    async def ejecutar(self, email: str, password: str) -> str:
        usuario = await self._repo.obtener_por_email(email)
        if usuario is None or not self._hasher.verificar(password, usuario.password_hash):
            raise CredencialesInvalidas("Email o contrasena incorrectos")
        if not usuario.activo:
            raise UsuarioInactivo(f"El usuario '{email}' esta inactivo")

        return self._tokens.crear_token(str(usuario.id), usuario.rol.value)


class ObtenerUsuarioAutenticado:
    def __init__(self, repo: UsuarioRepository, tokens: TokenService):
        self._repo = repo
        self._tokens = tokens

    async def ejecutar(self, token: str) -> Usuario:
        payload = self._tokens.decodificar_token(token)
        usuario = await self._repo.obtener_por_id(UUID(payload["sub"]))
        if usuario is None:
            raise UsuarioNoEncontrado("El usuario del token ya no existe")
        return usuario


class CrearUsuario:
    def __init__(self, repo: UsuarioRepository, hasher: PasswordHasher):
        self._repo = repo
        self._hasher = hasher

    async def ejecutar(self, email: str, password: str, rol: RolUsuario) -> Usuario:
        existente = await self._repo.obtener_por_email(email)
        if existente is not None:
            raise EmailDuplicado(f"Ya existe un usuario con el email '{email}'")

        usuario = Usuario(email=email, password_hash=self._hasher.hashear(password), rol=rol)
        return await self._repo.crear(usuario)
