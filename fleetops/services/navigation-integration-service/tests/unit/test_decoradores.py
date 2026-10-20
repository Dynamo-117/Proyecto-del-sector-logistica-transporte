import pytest

from app.domain.entities import Coordenada, Ruta
from app.domain.exceptions import ProveedorNoDisponible, SinRutaEncontrada
from app.infrastructure.external.decoradores import (
    CacheNavigationProvider,
    NavigationProviderDecorator,
    RegistroNavigationProvider,
    ReintentosNavigationProvider,
    decorar_proveedor,
)

A = Coordenada(latitud=4.71, longitud=-74.07)
B = Coordenada(latitud=6.25, longitud=-75.56)
C = Coordenada(latitud=3.45, longitud=-76.53)
RUTA = Ruta(origen=A, destino=B, distancia_km=415.0, duracion_min=300.0, puntos=[A, B])


class ProveedorFalso:
    """Cuenta las llamadas y falla las primeras `fallos_iniciales` veces."""

    def __init__(self, fallos_iniciales: int = 0, error=ProveedorNoDisponible):
        self.llamadas = 0
        self.cerrado = False
        self._fallos = fallos_iniciales
        self._error = error

    async def calcular_ruta(self, origen, destino) -> Ruta:
        self.llamadas += 1
        if self.llamadas <= self._fallos:
            raise self._error("fallo simulado")
        return Ruta(origen=origen, destino=destino, distancia_km=1.0, duracion_min=1.0, puntos=[])

    async def cerrar(self) -> None:
        self.cerrado = True


class Reloj:
    def __init__(self):
        self.ahora = 0.0

    def __call__(self) -> float:
        return self.ahora


async def _sin_espera(_: float) -> None:
    return None


async def test_decorador_base_delega_todo_en_el_envuelto():
    base = ProveedorFalso()
    decorado = NavigationProviderDecorator(base)

    await decorado.calcular_ruta(A, B)
    await decorado.cerrar()

    assert base.llamadas == 1
    assert base.cerrado


async def test_cache_no_vuelve_a_consultar_al_proveedor_para_el_mismo_trayecto():
    base = ProveedorFalso()
    cache = CacheNavigationProvider(base)

    primera = await cache.calcular_ruta(A, B)
    segunda = await cache.calcular_ruta(A, B)

    assert base.llamadas == 1
    assert segunda is primera
    assert (cache.aciertos, cache.fallos) == (1, 1)


async def test_cache_distingue_trayectos_distintos():
    base = ProveedorFalso()
    cache = CacheNavigationProvider(base)

    await cache.calcular_ruta(A, B)
    await cache.calcular_ruta(A, C)

    assert base.llamadas == 2


async def test_cache_expira_pasado_el_ttl():
    base = ProveedorFalso()
    reloj = Reloj()
    cache = CacheNavigationProvider(base, ttl_segundos=60, reloj=reloj)

    await cache.calcular_ruta(A, B)
    reloj.ahora = 61
    await cache.calcular_ruta(A, B)

    assert base.llamadas == 2


async def test_cache_descarta_la_entrada_mas_antigua_al_llenarse():
    base = ProveedorFalso()
    cache = CacheNavigationProvider(base, max_entradas=1)

    await cache.calcular_ruta(A, B)
    await cache.calcular_ruta(A, C)
    await cache.calcular_ruta(A, B)

    assert base.llamadas == 3


async def test_cache_no_guarda_los_fallos():
    base = ProveedorFalso(fallos_iniciales=1)
    cache = CacheNavigationProvider(base)

    with pytest.raises(ProveedorNoDisponible):
        await cache.calcular_ruta(A, B)
    await cache.calcular_ruta(A, B)

    assert base.llamadas == 2


async def test_reintentos_se_recupera_tras_fallos_transitorios():
    base = ProveedorFalso(fallos_iniciales=2)
    esperas: list[float] = []

    async def dormir(segundos: float) -> None:
        esperas.append(segundos)

    proveedor = ReintentosNavigationProvider(base, intentos=3, espera_segundos=0.5, dormir=dormir)

    await proveedor.calcular_ruta(A, B)

    assert base.llamadas == 3
    assert esperas == [0.5, 1.0]


async def test_reintentos_se_rinde_tras_agotar_los_intentos():
    base = ProveedorFalso(fallos_iniciales=99)
    proveedor = ReintentosNavigationProvider(base, intentos=3, dormir=_sin_espera)

    with pytest.raises(ProveedorNoDisponible):
        await proveedor.calcular_ruta(A, B)

    assert base.llamadas == 3


async def test_reintentos_no_reintenta_un_no_hay_camino():
    base = ProveedorFalso(fallos_iniciales=99, error=SinRutaEncontrada)
    proveedor = ReintentosNavigationProvider(base, intentos=3, dormir=_sin_espera)

    with pytest.raises(SinRutaEncontrada):
        await proveedor.calcular_ruta(A, B)

    assert base.llamadas == 1


async def test_registro_devuelve_la_ruta_y_propaga_los_errores():
    reloj = Reloj()
    ok = RegistroNavigationProvider(ProveedorFalso(), "falso", reloj=reloj)
    roto = RegistroNavigationProvider(ProveedorFalso(fallos_iniciales=1), "roto", reloj=reloj)

    ruta = await ok.calcular_ruta(A, B)

    assert ruta.distancia_km == 1.0
    with pytest.raises(ProveedorNoDisponible):
        await roto.calcular_ruta(A, B)


async def test_los_decoradores_se_apilan_y_el_cierre_llega_al_proveedor_real():
    base = ProveedorFalso(fallos_iniciales=1)
    pila = decorar_proveedor(base, "falso")

    await pila.calcular_ruta(A, B)
    await pila.calcular_ruta(A, B)
    await pila.cerrar()

    assert base.llamadas == 2
    assert base.cerrado
