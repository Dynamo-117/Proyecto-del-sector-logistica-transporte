from __future__ import annotations

import asyncio
import time
from collections import deque
from collections.abc import Callable
from typing import Any, Protocol

from app.core.logging import get_logger

logger = get_logger(__name__)


class PublicadorReal(Protocol):
    """Lo que el Proxy necesita del Sujeto Real (RabbitMQPublisher)."""

    @property
    def esta_conectado(self) -> bool: ...

    async def conectar(self) -> None: ...

    async def desconectar(self) -> None: ...

    async def publicar(self, routing_key: str, payload: dict[str, Any]) -> None: ...


class PublicadorEventosProxy:
    # =================   PATRON GOF: PROXY -- inicia aqui =================
    """El Proxy: se hace pasar por el publicador de eventos (misma interfaz
    EventPublisher) y controla el acceso al Sujeto Real, que es una conexion
    remota a RabbitMQ.

    Los casos de uso llaman a publicar() como siempre, sin saber que hay un
    intermediario. El proxy decide cuando y como llegar al broker real:
      - Conexion perezosa y tolerante: si RabbitMQ no esta disponible al
        iniciar, el servicio arranca igual; se vuelve a intentar mas tarde,
        sin saturar al broker (no mas de un intento cada `espera_reintento_s`).
      - Si no puede entregar un evento, lo guarda en un buzon acotado en vez
        de hacer fallar la operacion de negocio (crear un vehiculo no debe
        fallar porque el broker este caido).
      - Cuando el broker vuelve, entrega los pendientes en el mismo orden.
    """

    def __init__(
        self,
        real: PublicadorReal,
        capacidad_pendientes: int = 1000,
        espera_reintento_s: float = 5.0,
        timeout_conexion_s: float = 3.0,
        reloj: Callable[[], float] = time.monotonic,
    ):
        self._real = real
        self._pendientes: deque[tuple[str, dict[str, Any]]] = deque(maxlen=capacidad_pendientes)
        self._espera = espera_reintento_s
        self._timeout = timeout_conexion_s
        self._reloj = reloj
        self._ultimo_intento = float("-inf")
        self.publicados = 0
        self.descartados = 0

    @property
    def esta_conectado(self) -> bool:
        return self._real.esta_conectado

    @property
    def pendientes(self) -> int:
        return len(self._pendientes)

    async def conectar(self) -> None:
        await self._asegurar_conexion(forzar=True)

    async def desconectar(self) -> None:
        await self._real.desconectar()

    async def publicar(self, routing_key: str, payload: dict[str, Any]) -> None:
        if len(self._pendientes) == self._pendientes.maxlen:
            self.descartados += 1
        self._pendientes.append((routing_key, payload))
        await self.entregar_pendientes()

    async def entregar_pendientes(self, forzar: bool = False) -> int:
        """Entrega en orden lo acumulado; devuelve cuantos eventos salieron."""
        if self._pendientes and not await self._asegurar_conexion(forzar):
            return 0

        entregados = 0
        while self._pendientes:
            routing_key, payload = self._pendientes[0]
            try:
                await self._real.publicar(routing_key, payload)
            except Exception as exc:
                logger.warning("evento_pendiente", routing_key=routing_key, error=str(exc))
                break
            self._pendientes.popleft()
            self.publicados += 1
            entregados += 1
        return entregados

    async def _asegurar_conexion(self, forzar: bool = False) -> bool:
        if self._real.esta_conectado:
            return True
        ahora = self._reloj()
        if not forzar and ahora - self._ultimo_intento < self._espera:
            return False
        self._ultimo_intento = ahora
        try:
            await asyncio.wait_for(self._real.conectar(), timeout=self._timeout)
        except Exception as exc:
            logger.warning("rabbitmq_no_disponible", error=str(exc))
            return False
        return self._real.esta_conectado

    # ================= PATRON GOF: PROXY -- termina aqui =================
