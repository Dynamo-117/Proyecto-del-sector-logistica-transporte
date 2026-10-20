from __future__ import annotations

from typing import Any

import httpx

from app.core.logging import get_logger
from app.domain.exceptions import ServicioNoDisponible

logger = get_logger(__name__)


class ClienteJson:
    """Hace GET a un microservicio y devuelve el JSON; un 404 devuelve None y
    cualquier otro fallo (red o 5xx) se traduce a ServicioNoDisponible."""

    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def obtener(self, url: str, headers: dict[str, str]) -> Any | None:
        try:
            respuesta = await self._client.get(url, headers=headers)
        except httpx.HTTPError as exc:
            logger.error("subsistema_no_alcanzable", url=url, error=str(exc))
            raise ServicioNoDisponible(f"No se pudo contactar {url}: {exc}") from exc
        if respuesta.status_code == 404:
            return None
        if respuesta.status_code >= 400:
            raise ServicioNoDisponible(f"{url} respondio {respuesta.status_code}")
        return respuesta.json()


class FlotaHttp:
    def __init__(self, cliente: ClienteJson, base_url: str):
        self._cliente = cliente
        self._base = base_url

    async def listar_vehiculos(self, headers: dict[str, str]) -> list[dict[str, Any]]:
        return await self._cliente.obtener(f"{self._base}/vehiculos?limit=500", headers) or []

    async def listar_conductores(self, headers: dict[str, str]) -> list[dict[str, Any]]:
        return await self._cliente.obtener(f"{self._base}/conductores?limit=500", headers) or []


class RutasHttp:
    def __init__(self, cliente: ClienteJson, base_url: str):
        self._cliente = cliente
        self._base = base_url

    async def listar_rutas_activas(self, headers: dict[str, str]) -> list[dict[str, Any]]:
        return await self._cliente.obtener(f"{self._base}/rutas", headers) or []


class MantenimientoHttp:
    def __init__(self, cliente: ClienteJson, base_url: str):
        self._cliente = cliente
        self._base = base_url

    async def contar_alertas_activas(self, vehiculo_id: str, headers: dict[str, str]) -> int:
        alertas = await self._cliente.obtener(
            f"{self._base}/vehiculos/{vehiculo_id}/alertas", headers
        )
        return len(alertas or [])


class TrackingHttp:
    def __init__(self, cliente: ClienteJson, base_url: str):
        self._cliente = cliente
        self._base = base_url

    async def estado_movimiento(self, vehiculo_id: str, headers: dict[str, str]) -> str | None:
        estado = await self._cliente.obtener(
            f"{self._base}/vehiculos/{vehiculo_id}/estado", headers
        )
        return None if estado is None else estado["estado_movimiento"]
