import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import correlation_id_var

CORRELATION_ID_HEADER = b"x-correlation-id"


class CorrelationIdMiddleware:
    """Middleware ASGI puro (no BaseHTTPMiddleware): BaseHTTPMiddleware envuelve
    el canal de recepcion en un stream propio, lo que rompe request.is_disconnected()
    y respuestas de larga duracion (streaming/SSE) en otros servicios del monorepo
    que comparten este mismo middleware."""

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
