from __future__ import annotations

from collections.abc import AsyncIterator


class FakeRespuestaBackend:
    def __init__(
        self, status_code: int = 200, headers: dict[str, str] | None = None, body: bytes = b""
    ):
        self.status_code = status_code
        self.headers = headers or {}
        self._body = body
        self.cerrada = False

    async def aiter_raw(self) -> AsyncIterator[bytes]:
        yield self._body

    async def aclose(self) -> None:
        self.cerrada = True


class FakeProxyClient:
    def __init__(self, respuesta: FakeRespuestaBackend | None = None):
        self.respuesta = respuesta or FakeRespuestaBackend()
        self.llamadas: list[tuple[str, str, dict, dict, bytes]] = []

    async def enviar(
        self, method: str, url: str, headers: dict[str, str], params: dict[str, str], content: bytes
    ) -> FakeRespuestaBackend:
        self.llamadas.append((method, url, headers, params, content))
        return self.respuesta
