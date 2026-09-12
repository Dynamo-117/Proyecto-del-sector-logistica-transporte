from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.domain.exceptions import TokenInvalido


class JWTTokenService:
    def __init__(self, secret_key: str, algorithm: str = "HS256", expire_minutos: int = 60):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expire_minutos = expire_minutos

    def crear_token(self, usuario_id: str, rol: str) -> str:
        ahora = datetime.now(UTC)
        payload = {
            "sub": usuario_id,
            "rol": rol,
            "iat": ahora,
            "exp": ahora + timedelta(minutes=self._expire_minutos),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decodificar_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.PyJWTError as exc:
            raise TokenInvalido("Token invalido o expirado") from exc
