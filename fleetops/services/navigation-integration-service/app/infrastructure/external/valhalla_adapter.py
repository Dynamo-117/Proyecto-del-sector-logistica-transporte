from __future__ import annotations

import httpx

from app.core.logging import get_logger
from app.domain.entities import Coordenada, Ruta
from app.domain.exceptions import ProveedorNoDisponible, SinRutaEncontrada
from app.domain.ruta_builder import RutaBuilder
from app.infrastructure.external.valhalla_api import ValhallaApi, ValhallaApiError

logger = get_logger(__name__)


def decodificar_polyline(codificada: str, precision: int = 6) -> list[tuple[float, float]]:
    """Decodifica una polyline (algoritmo de Google; Valhalla usa 6 decimales).
    Devuelve pares (latitud, longitud)."""
    factor = 10**precision
    puntos: list[tuple[float, float]] = []
    indice, lat, lon = 0, 0, 0

    while indice < len(codificada):
        valores = []
        for _ in range(2):
            desplazamiento, resultado = 0, 0
            while True:
                byte = ord(codificada[indice]) - 63
                indice += 1
                resultado |= (byte & 0x1F) << desplazamiento
                desplazamiento += 5
                if byte < 0x20:
                    break
            valores.append(~(resultado >> 1) if resultado & 1 else resultado >> 1)
        lat += valores[0]
        lon += valores[1]
        puntos.append((lat / factor, lon / factor))

    return puntos


class ValhallaNavigationAdapter:
    # =================   PATRON GOF: ADAPTER -- inicia aqui =================
    """El Adaptador: implementa la interfaz que el sistema espera (Objetivo =
    NavigationProvider) y por dentro delega en el Adaptado (ValhallaApi),
    traduciendo en ambos sentidos: Coordenada -> numeros sueltos de entrada, y
    "trip" de Valhalla (km, segundos, polyline6) -> Ruta del dominio (km, minutos,
    lista de Coordenada) de salida. El caso de uso CalcularRuta no sabe que
    detras hay un proveedor con una API completamente distinta a la de OSRM.
    """

    def __init__(self, api: ValhallaApi):
        self._api = api

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        try:
            viaje = await self._api.obtener_viaje(
                origen.latitud, origen.longitud, destino.latitud, destino.longitud
            )
        except ValhallaApiError as exc:
            if exc.status_code < 500:
                raise SinRutaEncontrada(
                    f"El proveedor de rutas no pudo trazar el camino: {exc.mensaje}"
                ) from exc
            logger.error("valhalla_respuesta_no_ok", status_code=exc.status_code)
            raise ProveedorNoDisponible(
                f"El proveedor de rutas respondio con status {exc.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("valhalla_no_alcanzable", error=str(exc))
            raise ProveedorNoDisponible(
                f"No se pudo contactar al proveedor de rutas: {exc}"
            ) from exc

        resumen = viaje["summary"]
        geometria = [
            (lon, lat)
            for tramo in viaje["legs"]
            for lat, lon in decodificar_polyline(tramo["shape"])
        ]

        return (
            RutaBuilder()
            .con_extremos(origen, destino)
            .con_metricas(
                distancia_metros=resumen["length"] * 1000, duracion_segundos=resumen["time"]
            )
            .con_geometria(geometria)
            .construir()
        )

    async def cerrar(self) -> None:
        await self._api.cerrar()

    # ================= PATRON GOF: ADAPTER -- termina aqui =================
