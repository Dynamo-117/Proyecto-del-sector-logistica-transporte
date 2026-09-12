from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Protocol


class RespuestaBackend(Protocol):
    """Subconjunto de httpx.Response que necesita el gateway para transmitir
    la respuesta del servicio destino sin cargarla completa en memoria."""

    status_code: int
    headers: Mapping[str, str]

    def aiter_raw(self) -> AsyncIterator[bytes]: ...

    async def aclose(self) -> None: ...


class ProxyClient(Protocol):
    async def enviar(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, str],
        content: bytes,
    ) -> RespuestaBackend: ...
