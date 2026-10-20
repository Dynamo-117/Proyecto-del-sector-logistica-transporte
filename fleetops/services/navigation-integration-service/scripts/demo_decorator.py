"""Demostracion del patron DECORATOR en navigation-integration-service.

  1) Reintentos: un proveedor que falla dos veces se recupera solo.
  2) Cache: la segunda consulta del mismo trayecto no llega al proveedor externo.
  3) Pila completa: registro(cache(reintentos(proveedor real))) sobre OSRM real.

Las partes 2 y 3 consultan al servidor publico de OSRM (requiere internet).

Uso (desde services/navigation-integration-service, con el entorno virtual activo):
    python -m scripts.demo_decorator
"""

import asyncio
import time

from app.core.config import get_settings
from app.domain.entities import Coordenada, Ruta
from app.domain.exceptions import ProveedorNoDisponible
from app.infrastructure.external.decoradores import (
    CacheNavigationProvider,
    ReintentosNavigationProvider,
    decorar_proveedor,
)
from app.infrastructure.external.osrm_client import OSRMClient

BOGOTA = Coordenada(latitud=4.7110, longitud=-74.0721)
MEDELLIN = Coordenada(latitud=6.2442, longitud=-75.5812)
CALI = Coordenada(latitud=3.4516, longitud=-76.5320)


class ProveedorInestable:
    """Falla las primeras `fallos` llamadas y despues responde bien."""

    def __init__(self, fallos: int):
        self.llamadas = 0
        self._fallos = fallos

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        self.llamadas += 1
        if self.llamadas <= self._fallos:
            print(f"      llamada #{self.llamadas} al proveedor -> FALLA (proveedor caido)")
            raise ProveedorNoDisponible("simulado")
        print(f"      llamada #{self.llamadas} al proveedor -> OK")
        return Ruta(
            origen=origen, destino=destino, distancia_km=415.0, duracion_min=300.0, puntos=[]
        )


class ContadorOSRM:
    """Cuenta cuantas veces se llega de verdad al servidor externo."""

    def __init__(self, osrm: OSRMClient):
        self._osrm = osrm
        self.llamadas = 0

    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        self.llamadas += 1
        return await self._osrm.calcular_ruta(origen, destino)

    async def cerrar(self) -> None:
        await self._osrm.cerrar()


async def medir(proveedor, origen, destino) -> tuple[Ruta, float]:
    inicio = time.perf_counter()
    ruta = await proveedor.calcular_ruta(origen, destino)
    return ruta, (time.perf_counter() - inicio) * 1000


async def main() -> None:
    print("PATRON DECORATOR -- navigation-integration-service\n")

    print("1) ReintentosNavigationProvider sobre un proveedor que falla 2 veces:")
    inestable = ProveedorInestable(fallos=2)
    con_reintentos = ReintentosNavigationProvider(inestable, intentos=3, espera_segundos=0.2)
    ruta, ms = await medir(con_reintentos, BOGOTA, MEDELLIN)
    resumen = f"{ruta.distancia_km} km tras {inestable.llamadas} llamadas ({ms:.0f} ms)"
    print(f"   -> resultado: {resumen}\n")

    print("2) CacheNavigationProvider (misma interfaz, comportamiento agregado):")
    contador = ContadorOSRM(OSRMClient(get_settings().osrm_base_url))
    con_cache = CacheNavigationProvider(contador)
    try:
        for etiqueta, destino in (
            ("Bogota->Medellin (1ra vez)", MEDELLIN),
            ("Bogota->Medellin (2da vez)", MEDELLIN),
            ("Bogota->Cali     (1ra vez)", CALI),
        ):
            _, ms = await medir(con_cache, BOGOTA, destino)
            print(f"   {etiqueta}  {ms:>8.1f} ms   llamadas reales a OSRM: {contador.llamadas}")
    except Exception as error:
        print(f"   No se pudo consultar OSRM ({type(error).__name__}): {error}")
    print(f"   aciertos de cache = {con_cache.aciertos}, fallos = {con_cache.fallos}\n")
    await contador.cerrar()

    print("3) Pila completa armada con decorar_proveedor(): registro(cache(reintentos(OSRM))):")
    pila = decorar_proveedor(OSRMClient(get_settings().osrm_base_url), "osrm")
    try:
        for veces in (1, 2):
            _, ms = await medir(pila, BOGOTA, MEDELLIN)
            print(f"   consulta #{veces}: {ms:.1f} ms")
    except Exception as error:
        print(f"   No se pudo consultar OSRM ({type(error).__name__}): {error}")
    await pila.cerrar()

    print(
        "\nRESULTADO: reintentos, cache y registro se apilan sobre cualquier proveedor sin tocarlo."
    )


if __name__ == "__main__":
    asyncio.run(main())
