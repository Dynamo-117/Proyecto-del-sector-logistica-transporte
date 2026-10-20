from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable

from app.application.ports.navigation import NavigationProvider
from app.core.logging import get_logger
from app.domain.entities import Coordenada, Ruta
from app.domain.exceptions import ProveedorNoDisponible

logger = get_logger(__name__)


class NavigationProviderDecorator:
    # =================   PATRON GOF: DECORATOR -- inicia aqui =================
    """El Decorador base: implementa la misma interfaz que el componente que
    envuelve (NavigationProvider) y, por defecto, le delega todo. Cada
    decorador concreto sobreescribe calcular_ruta() para agregar su
    comportamiento antes y/o despues de delegar, sin que el cliente (el caso de
    uso CalcularRuta) ni el proveedor envuelto se enteren.
    """

    def __init__(self, envuelto: NavigationProvider):
        self._envuelto = envuelto

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        return await self._envuelto.calcular_ruta(origen, destino)

    async def cerrar(self) -> None:
        cerrar = getattr(self._envuelto, "cerrar", None)
        if cerrar is not None:
            await cerrar()


class ReintentosNavigationProvider(NavigationProviderDecorator):
    """Decorador concreto: reintenta con espera creciente cuando el proveedor
    esta caido (ProveedorNoDisponible). Un "no hay camino" no se reintenta."""

    def __init__(
        self,
        envuelto: NavigationProvider,
        intentos: int = 3,
        espera_segundos: float = 0.5,
        dormir: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ):
        super().__init__(envuelto)
        self._intentos = intentos
        self._espera = espera_segundos
        self._dormir = dormir

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        for intento in range(1, self._intentos + 1):
            try:
                return await self._envuelto.calcular_ruta(origen, destino)
            except ProveedorNoDisponible:
                if intento == self._intentos:
                    raise
                espera = self._espera * 2 ** (intento - 1)
                logger.warning("reintentando_proveedor", intento=intento, espera_s=espera)
                await self._dormir(espera)
        raise AssertionError("inalcanzable")


class CacheNavigationProvider(NavigationProviderDecorator):
    """Decorador concreto: recuerda las rutas ya calculadas (mismo origen y
    destino) durante un tiempo, para no volver a consultar al proveedor externo."""

    def __init__(
        self,
        envuelto: NavigationProvider,
        ttl_segundos: float = 300.0,
        max_entradas: int = 256,
        reloj: Callable[[], float] = time.monotonic,
    ):
        super().__init__(envuelto)
        self._ttl = ttl_segundos
        self._max = max_entradas
        self._reloj = reloj
        self._entradas: dict[tuple[float, float, float, float], tuple[float, Ruta]] = {}
        self.aciertos = 0
        self.fallos = 0

    @staticmethod
    def _clave(origen: Coordenada, destino: Coordenada) -> tuple[float, float, float, float]:
        return (
            round(origen.latitud, 5),
            round(origen.longitud, 5),
            round(destino.latitud, 5),
            round(destino.longitud, 5),
        )

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        clave = self._clave(origen, destino)
        ahora = self._reloj()

        guardada = self._entradas.get(clave)
        if guardada is not None and ahora - guardada[0] < self._ttl:
            self.aciertos += 1
            return guardada[1]

        self.fallos += 1
        ruta = await self._envuelto.calcular_ruta(origen, destino)

        if len(self._entradas) >= self._max:
            del self._entradas[next(iter(self._entradas))]
        self._entradas[clave] = (ahora, ruta)
        return ruta


class RegistroNavigationProvider(NavigationProviderDecorator):
    """Decorador concreto: deja en el log cuanto tardo cada calculo y si fallo."""

    def __init__(
        self,
        envuelto: NavigationProvider,
        nombre: str,
        reloj: Callable[[], float] = time.perf_counter,
    ):
        super().__init__(envuelto)
        self._nombre = nombre
        self._reloj = reloj

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        inicio = self._reloj()
        try:
            ruta = await self._envuelto.calcular_ruta(origen, destino)
        except Exception as exc:
            logger.warning(
                "ruta_fallida",
                proveedor=self._nombre,
                error=type(exc).__name__,
                duracion_ms=round((self._reloj() - inicio) * 1000, 1),
            )
            raise
        logger.info(
            "ruta_calculada",
            proveedor=self._nombre,
            distancia_km=round(ruta.distancia_km, 1),
            duracion_ms=round((self._reloj() - inicio) * 1000, 1),
        )
        return ruta

    # ================= PATRON GOF: DECORATOR -- termina aqui =================


def decorar_proveedor(base: NavigationProvider, nombre: str) -> NavigationProviderDecorator:
    """Apila los decoradores de afuera hacia adentro: registro(cache(reintentos(base)))."""
    return RegistroNavigationProvider(
        CacheNavigationProvider(ReintentosNavigationProvider(base)), nombre
    )
