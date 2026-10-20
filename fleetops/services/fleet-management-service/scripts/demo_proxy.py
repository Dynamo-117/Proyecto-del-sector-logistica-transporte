"""Demostracion del patron PROXY en fleet-management-service.

Se simula un RabbitMQ que primero esta caido y luego vuelve, y se muestra que
el Proxy deja que el servicio siga funcionando: los eventos que no pueden
entregarse quedan pendientes y salen, en orden, cuando el broker regresa.
No requiere RabbitMQ ni ningun otro servicio.

Uso (desde services/fleet-management-service, con el entorno virtual activo):
    python -m scripts.demo_proxy
"""

import asyncio
from typing import Any

from app.infrastructure.messaging.publicador_proxy import PublicadorEventosProxy


class BrokerSimulado:
    """El Sujeto Real: un broker remoto que puede estar caido."""

    def __init__(self) -> None:
        self.disponible = False
        self._conectado = False
        self.entregados: list[str] = []

    @property
    def esta_conectado(self) -> bool:
        return self._conectado

    async def conectar(self) -> None:
        if not self.disponible:
            raise ConnectionError("conexion rechazada (puerto 5672)")
        self._conectado = True

    async def desconectar(self) -> None:
        self._conectado = False

    async def publicar(self, routing_key: str, payload: dict[str, Any]) -> None:
        self.entregados.append(f"{routing_key} {payload['placa']}")


def estado(proxy: PublicadorEventosProxy) -> str:
    return (
        f"conectado={proxy.esta_conectado!s:<5}  pendientes={proxy.pendientes}"
        f"  publicados={proxy.publicados}"
    )


async def crear_vehiculo(proxy: PublicadorEventosProxy, placa: str) -> None:
    """Lo mismo que hace el caso de uso CrearVehiculo: publicar y seguir."""
    await proxy.publicar("vehiculo.creado", {"placa": placa})
    print(f"   crear vehiculo {placa}: OK (la operacion no fallo)   -> {estado(proxy)}")


async def main() -> None:
    print("PATRON PROXY -- fleet-management-service\n")
    broker = BrokerSimulado()
    proxy = PublicadorEventosProxy(broker, espera_reintento_s=60)

    print("1) El broker esta caido y el servicio arranca igual:")
    await proxy.conectar()
    print(f"   inicio del servicio: sin excepcion   -> {estado(proxy)}\n")

    print("2) Se crean vehiculos con el broker caido (el proxy los guarda):")
    for placa in ("TRK001", "TRK002", "TRK003"):
        await crear_vehiculo(proxy, placa)

    print("\n3) El broker vuelve y el proxy entrega los pendientes en orden:")
    broker.disponible = True
    entregados = await proxy.entregar_pendientes(forzar=True)
    print(f"   reintento: {entregados} eventos entregados          -> {estado(proxy)}")
    for evento in broker.entregados:
        print(f"      el broker recibio: {evento}")

    print("\n4) Con el broker disponible, el proxy deja pasar los eventos directamente:")
    await crear_vehiculo(proxy, "TRK004")
    print(f"      el broker recibio: {broker.entregados[-1]}")

    print("\nRESULTADO: el broker caido no hizo fallar nada y no se perdio ningun evento.")


if __name__ == "__main__":
    asyncio.run(main())
