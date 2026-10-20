from __future__ import annotations

import asyncio
from collections import Counter
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from app.application.ports.subsistemas import FlotaApi, MantenimientoApi, RutasApi, TrackingApi
from app.domain.resumen import (
    ResumenFlota,
    ResumenMantenimiento,
    ResumenOperativo,
    ResumenRutas,
    ResumenTracking,
)

T = TypeVar("T")

MAX_CONSULTAS_SIMULTANEAS = 8


class ResumenOperativoFacade:
    # =================   PATRON GOF: FACADE -- inicia aqui =================
    """La Fachada: ofrece una unica operacion simple (obtener) que esconde un
    subsistema complejo -- cuatro microservicios con APIs distintas, que hay
    que consultar en cierto orden y a veces una vez por vehiculo. El cliente
    (la ruta GET /resumen, y detras el frontend) no conoce a ninguno de los
    subsistemas: llama una vez y recibe el resumen ya armado.

    La fachada ademas coordina la parte incomoda de ese subsistema: lanza las
    consultas en paralelo, limita cuantas hay a la vez y tolera que un
    servicio este caido (esa seccion se marca como no disponible en vez de
    hacer fallar todo el resumen).
    """

    def __init__(
        self,
        flota: FlotaApi,
        rutas: RutasApi,
        mantenimiento: MantenimientoApi,
        tracking: TrackingApi,
    ):
        self._flota = flota
        self._rutas = rutas
        self._mantenimiento = mantenimiento
        self._tracking = tracking

    async def obtener(self, headers: dict[str, str]) -> ResumenOperativo:
        llamadas = 0

        async def consultar(operacion: Callable[[], Awaitable[T]]) -> T:
            nonlocal llamadas
            llamadas += 1
            return await operacion()

        (vehiculos, conductores, rutas) = await asyncio.gather(
            consultar(lambda: self._flota.listar_vehiculos(headers)),
            consultar(lambda: self._flota.listar_conductores(headers)),
            consultar(lambda: self._rutas.listar_rutas_activas(headers)),
            return_exceptions=True,
        )

        flota = self._armar_flota(vehiculos, conductores)
        resumen_rutas = self._armar_rutas(rutas)

        ids = [v["id"] for v in vehiculos] if isinstance(vehiculos, list) else []
        limite = asyncio.Semaphore(MAX_CONSULTAS_SIMULTANEAS)

        async def acotada(operacion: Callable[[], Awaitable[T]]) -> T:
            async with limite:
                return await consultar(operacion)

        alertas, estados = await asyncio.gather(
            asyncio.gather(
                *(
                    acotada(lambda i=i: self._mantenimiento.contar_alertas_activas(i, headers))
                    for i in ids
                ),
                return_exceptions=True,
            ),
            asyncio.gather(
                *(acotada(lambda i=i: self._tracking.estado_movimiento(i, headers)) for i in ids),
                return_exceptions=True,
            ),
        )

        return ResumenOperativo(
            flota=flota,
            rutas=resumen_rutas,
            mantenimiento=self._armar_mantenimiento(alertas, flota),
            tracking=self._armar_tracking(estados, flota),
            llamadas_internas=llamadas,
        )

    @staticmethod
    def _armar_flota(vehiculos: Any, conductores: Any) -> ResumenFlota:
        if not isinstance(vehiculos, list) or not isinstance(conductores, list):
            return ResumenFlota(disponible=False)
        return ResumenFlota(
            disponible=True,
            total_vehiculos=len(vehiculos),
            vehiculos_por_estado=dict(Counter(v["estado"] for v in vehiculos)),
            total_conductores=len(conductores),
            conductores_disponibles=sum(1 for c in conductores if c["estado"] == "DISPONIBLE"),
        )

    @staticmethod
    def _armar_rutas(rutas: Any) -> ResumenRutas:
        if not isinstance(rutas, list):
            return ResumenRutas(disponible=False)
        return ResumenRutas(
            disponible=True,
            rutas_activas=len(rutas),
            distancia_total_km=round(sum(r["distancia_km"] for r in rutas), 1),
        )

    @staticmethod
    def _armar_mantenimiento(resultados: list[Any], flota: ResumenFlota) -> ResumenMantenimiento:
        if not flota.disponible or any(isinstance(r, Exception) for r in resultados):
            return ResumenMantenimiento(disponible=False)
        return ResumenMantenimiento(
            disponible=True,
            alertas_activas=sum(resultados),
            vehiculos_con_alertas=sum(1 for r in resultados if r > 0),
        )

    @staticmethod
    def _armar_tracking(resultados: list[Any], flota: ResumenFlota) -> ResumenTracking:
        if not flota.disponible or any(isinstance(r, Exception) for r in resultados):
            return ResumenTracking(disponible=False)
        return ResumenTracking(
            disponible=True,
            en_movimiento=sum(1 for r in resultados if r == "EN_MOVIMIENTO"),
            detenidos=sum(1 for r in resultados if r == "DETENIDO"),
            sin_telemetria=sum(1 for r in resultados if r is None),
        )

    # ================= PATRON GOF: FACADE -- termina aqui =================
