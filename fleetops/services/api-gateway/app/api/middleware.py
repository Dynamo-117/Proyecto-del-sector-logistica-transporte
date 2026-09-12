import json
import re
import uuid

import jwt
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import correlation_id_var

CORRELATION_ID_HEADER = b"x-correlation-id"


class CorrelationIdMiddleware:
    """Middleware ASGI puro (no BaseHTTPMiddleware): BaseHTTPMiddleware envuelve
    el canal de recepcion en un stream propio, lo que rompe request.is_disconnected()
    y respuestas de larga duracion (streaming/SSE) reenviadas a traves del gateway."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        correlation_id = headers.get(CORRELATION_ID_HEADER, b"").decode() or str(uuid.uuid4())
        token = correlation_id_var.set(correlation_id)

        async def send_con_correlation_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = [
                    *message.get("headers", []),
                    (CORRELATION_ID_HEADER, correlation_id.encode()),
                ]
            await send(message)

        try:
            await self.app(scope, receive, send_con_correlation_id)
        finally:
            correlation_id_var.reset(token)


RUTAS_PUBLICAS = {"/health", "/ready"}
LOGIN_PATH = "/fleet/auth/login"

# Editar (PATCH) o eliminar (DELETE) un vehiculo/conductor puntual requiere rol
# ADMINISTRADOR. Crear (POST) y asignar/desasignar conductor (POST, subruta
# aparte) quedan abiertos a OPERADOR: son "operaciones normales" segun los
# roles definidos, no acciones destructivas ni de edicion de datos existentes.
_RUTA_ITEM_VEHICULO_O_CONDUCTOR = re.compile(r"^/fleet/(vehiculos|conductores)/[^/]+$")
_METODOS_QUE_REQUIEREN_ADMIN = {"PATCH", "DELETE"}


def _es_ruta_publica(method: str, path: str) -> bool:
    if path in RUTAS_PUBLICAS:
        return True
    return method == "POST" and path == LOGIN_PATH


def _requiere_rol_administrador(method: str, path: str) -> bool:
    return method in _METODOS_QUE_REQUIEREN_ADMIN and bool(
        _RUTA_ITEM_VEHICULO_O_CONDUCTOR.match(path)
    )


async def _enviar_error(send: Send, status_code: int, codigo: str, mensaje: str) -> None:
    body = json.dumps({"codigo": codigo, "mensaje": mensaje, "detalle": None}).encode()
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send({"type": "http.response.body", "body": body})


class JWTAuthMiddleware:
    """Middleware ASGI puro (no BaseHTTPMiddleware, ver CorrelationIdMiddleware
    arriba): valida el JWT firmado por fleet-management-service en cada
    peticion, salvo /health, /ready y POST /fleet/auth/login."""

    def __init__(self, app: ASGIApp, secret_key: str, algorithm: str = "HS256"):
        self.app = app
        self._secret_key = secret_key
        self._algorithm = algorithm

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        path = scope["path"]

        if _es_ruta_publica(method, path):
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        auth_header = headers.get(b"authorization", b"").decode()
        if not auth_header.lower().startswith("bearer "):
            await _enviar_error(send, 401, "NO_AUTENTICADO", "Falta el header Authorization Bearer")
            return

        token = auth_header[len("Bearer ") :]
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.PyJWTError:
            await _enviar_error(send, 401, "TOKEN_INVALIDO", "Token invalido o expirado")
            return

        rol = payload.get("rol")
        if _requiere_rol_administrador(method, path) and rol != "ADMINISTRADOR":
            await _enviar_error(
                send, 403, "ROL_NO_AUTORIZADO", "Esta operacion requiere rol ADMINISTRADOR"
            )
            return

        await self.app(scope, receive, send)
