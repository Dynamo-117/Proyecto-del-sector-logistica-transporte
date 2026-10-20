from __future__ import annotations

from typing import Any

import httpx

VALHALLA_URL_POR_DEFECTO = "https://valhalla1.openstreetmap.de"


class ValhallaApiError(Exception):
    """Respuesta de error de la API de Valhalla (status HTTP distinto de 200)."""

    def __init__(self, status_code: int, mensaje: str):
        self.status_code = status_code
        self.mensaje = mensaje
        super().__init__(f"Valhalla respondio {status_code}: {mensaje}")


class ValhallaApi:
    # =================   PATRON GOF: ADAPTER (Adaptado) -- inicia aqui =================
    """El Adaptado (Adaptee): cliente crudo de la API publica de Valhalla
    (OpenStreetMap). Su interfaz es incompatible con NavigationProvider: recibe
    cuatro numeros sueltos en vez de dos Coordenada, devuelve el diccionario
    "trip" de Valhalla (distancia en km, tiempo en segundos, geometria como
    polyline codificada) y no conoce ninguna entidad del dominio de FleetOps.
    """

    def __init__(
        self,
        base_url: str = VALHALLA_URL_POR_DEFECTO,
        client: httpx.AsyncClient | None = None,
        timeout: float = 15.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(timeout=timeout)

    async def obtener_viaje(
        self, lat_origen: float, lon_origen: float, lat_destino: float, lon_destino: float
    ) -> dict[str, Any]:
        cuerpo = {
            "locations": [
                {"lat": lat_origen, "lon": lon_origen},
                {"lat": lat_destino, "lon": lon_destino},
            ],
            "costing": "auto",
            "directions_options": {"units": "kilometers"},
        }
        respuesta = await self._client.post(f"{self._base_url}/route", json=cuerpo)
        if respuesta.status_code != 200:
            try:
                mensaje = respuesta.json().get("error", respuesta.text)
            except ValueError:
                mensaje = respuesta.text
            raise ValhallaApiError(respuesta.status_code, str(mensaje))
        return respuesta.json()["trip"]

    async def cerrar(self) -> None:
        await self._client.aclose()

    # ================= PATRON GOF: ADAPTER (Adaptado) -- termina aqui =================
