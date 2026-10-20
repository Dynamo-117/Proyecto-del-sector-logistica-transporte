"""Demostracion del patron FACADE en api-gateway.

Compara dos formas de obtener el resumen operativo de la flota contra cuatro
microservicios simulados:
  - SIN fachada: el cliente tiene que conocer cada servicio, sus rutas y repetir
    una consulta por vehiculo.
  - CON fachada: una sola llamada a ResumenOperativoFacade.obtener().
Despues apaga un servicio para mostrar que el resumen no se cae completo.
No requiere que los servicios reales esten corriendo.

Uso (desde services/api-gateway, con el entorno virtual activo):
    python -m scripts.demo_facade
"""

import asyncio
from typing import Any

from app.application.facade.resumen_operativo_facade import ResumenOperativoFacade
from app.domain.exceptions import ServicioNoDisponible

VEHICULOS = [
    {"id": "v1", "estado": "DISPONIBLE"},
    {"id": "v2", "estado": "EN_RUTA"},
    {"id": "v3", "estado": "EN_RUTA"},
    {"id": "v4", "estado": "MANTENIMIENTO"},
]


class Registro:
    """Cuenta las peticiones que llegan a cada microservicio simulado."""

    def __init__(self) -> None:
        self.peticiones: list[str] = []

    def anotar(self, texto: str) -> None:
        self.peticiones.append(texto)


class Flota:
    def __init__(self, registro: Registro):
        self._r = registro

    async def listar_vehiculos(self, headers: dict[str, str]) -> list[dict[str, Any]]:
        self._r.anotar("fleet       GET /vehiculos")
        return VEHICULOS

    async def listar_conductores(self, headers: dict[str, str]) -> list[dict[str, Any]]:
        self._r.anotar("fleet       GET /conductores")
        return [{"estado": "DISPONIBLE"}, {"estado": "ASIGNADO"}, {"estado": "ASIGNADO"}]


class Rutas:
    def __init__(self, registro: Registro, caido: bool = False):
        self._r, self._caido = registro, caido

    async def listar_rutas_activas(self, headers: dict[str, str]) -> list[dict[str, Any]]:
        self._r.anotar("routing     GET /rutas")
        if self._caido:
            raise ServicioNoDisponible("routing: conexion rechazada (puerto 8003)")
        return [{"distancia_km": 415.0}, {"distancia_km": 280.0}]


class Mantenimiento:
    def __init__(self, registro: Registro):
        self._r = registro

    async def contar_alertas_activas(self, vehiculo_id: str, headers: dict[str, str]) -> int:
        self._r.anotar(f"maintenance GET /vehiculos/{vehiculo_id}/alertas")
        return {"v1": 0, "v2": 2, "v3": 0, "v4": 1}[vehiculo_id]


class Tracking:
    def __init__(self, registro: Registro):
        self._r = registro

    async def estado_movimiento(self, vehiculo_id: str, headers: dict[str, str]) -> str | None:
        self._r.anotar(f"tracking    GET /vehiculos/{vehiculo_id}/estado")
        return {"v1": None, "v2": "EN_MOVIMIENTO", "v3": "DETENIDO", "v4": None}[vehiculo_id]


def fachada(registro: Registro, rutas_caido: bool = False) -> ResumenOperativoFacade:
    return ResumenOperativoFacade(
        Flota(registro), Rutas(registro, rutas_caido), Mantenimiento(registro), Tracking(registro)
    )


def imprimir(resumen) -> None:
    f, r, m, t = resumen.flota, resumen.rutas, resumen.mantenimiento, resumen.tracking
    print(
        f"   flota         : {f.total_vehiculos} vehiculos {f.vehiculos_por_estado}, "
        f"{f.conductores_disponibles}/{f.total_conductores} conductores disponibles"
    )
    print(
        "   rutas activas : "
        + (f"{r.rutas_activas} ({r.distancia_total_km} km)" if r.disponible else "NO DISPONIBLE")
    )
    print(
        f"   mantenimiento : {m.alertas_activas} alertas activas en "
        f"{m.vehiculos_con_alertas} vehiculos"
    )
    print(
        f"   tracking      : {t.en_movimiento} en movimiento, {t.detenidos} detenidos, "
        f"{t.sin_telemetria} sin telemetria"
    )


async def main() -> None:
    print("PATRON FACADE -- api-gateway\n")

    print("1) Lo que hay DETRAS de la fachada: cuatro servicios y muchas peticiones")
    registro = Registro()
    resumen = await fachada(registro).obtener({})
    for peticion in registro.peticiones:
        print(f"      {peticion}")
    print(f"   -> {len(registro.peticiones)} peticiones a 4 microservicios\n")

    print("2) Lo que ve el cliente: UNA llamada, el resumen ya armado")
    print("      GET /resumen")
    imprimir(resumen)
    print(f"   llamadas_internas = {resumen.llamadas_internas}\n")

    print("3) Si un servicio falla, la fachada responde igual (esa seccion se marca):")
    caido = await fachada(Registro(), rutas_caido=True).obtener({})
    imprimir(caido)

    print(
        "\nRESULTADO: el cliente hace 1 llamada y la fachada coordina las "
        f"{resumen.llamadas_internas} internas."
    )


if __name__ == "__main__":
    asyncio.run(main())
