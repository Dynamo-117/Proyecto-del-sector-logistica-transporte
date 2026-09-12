from __future__ import annotations

from typing import Any, Protocol


class PasswordHasher(Protocol):
    def hashear(self, password: str) -> str: ...

    def verificar(self, password: str, password_hash: str) -> bool: ...


class TokenService(Protocol):
    def crear_token(self, usuario_id: str, rol: str) -> str: ...

    def decodificar_token(self, token: str) -> dict[str, Any]:
        """Levanta TokenInvalido si la firma o la expiracion no son validas."""
        ...
