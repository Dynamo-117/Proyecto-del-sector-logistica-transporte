from __future__ import annotations

import httpx

from app.core.logging import get_logger
from app.domain.exceptions import ServicioNoDisponible

logger = get_logger(__name__)


class HttpxProxyClient:
    """Reenvia peticiones al servicio destino usando streaming real (no espera
    a tener toda la respuesta en memoria antes de empezar a devolverla), para
    poder atravesar tambien respuestas de larga duracion como el SSE de
    vehicle-tracking-service."""

    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def enviar(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        params: dict[str, str],
        content: bytes,
    ) -> httpx.Response:
        request = self._client.build_request(
            method, url, headers=headers, params=params, content=content
        )
        try:
            return await self._client.send(request, stream=True)
        except httpx.HTTPError as exc:
            logger.error("servicio_destino_no_alcanzable", url=url, error=str(exc))
            raise ServicioNoDisponible(f"No se pudo contactar el servicio destino: {exc}") from exc
