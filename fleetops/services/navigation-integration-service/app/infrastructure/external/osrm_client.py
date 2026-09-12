from __future__ import annotations

import httpx

from app.core.logging import get_logger
from app.domain.entities import Coordenada, Ruta
from app.domain.exceptions import ProveedorNoDisponible, SinRutaEncontrada
from app.infrastructure.external.ruta_director import RutaDirector

logger = get_logger(__name__)


class OSRMClient:


    def __init__(
        self, base_url: str, client: httpx.AsyncClient | None = None, timeout: float = 10.0
    ):
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self._director = RutaDirector()

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        url = (
            f"{self._base_url}/route/v1/driving/"
            f"{origen.longitud},{origen.latitud};{destino.longitud},{destino.latitud}"
        )
        params = {"overview": "full", "geometries": "geojson"}

        try:
            respuesta = await self._client.get(url, params=params)
        except httpx.HTTPError as exc:
            logger.error("osrm_no_alcanzable", error=str(exc))
            raise ProveedorNoDisponible(
                f"No se pudo contactar al proveedor de rutas: {exc}"
            ) from exc

        if respuesta.status_code != 200:
            logger.error("osrm_respuesta_no_ok", status_code=respuesta.status_code)
            raise ProveedorNoDisponible(
                f"El proveedor de rutas respondio con status {respuesta.status_code}"
            )

        datos = respuesta.json()
        if datos.get("code") != "Ok" or not datos.get("routes"):
            raise SinRutaEncontrada(
                "El proveedor de rutas no encontro un camino entre los puntos dados"
            )

        ruta_osrm = datos["routes"][0]
        return self._director.construir_desde_respuesta_osrm(origen, destino, ruta_osrm)

    async def cerrar(self) -> None:
        await self._client.aclose()
