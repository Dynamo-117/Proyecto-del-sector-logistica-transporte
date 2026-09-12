from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable

import aio_pika
from aio_pika import ExchangeType

from app.core.logging import get_logger

logger = get_logger(__name__)

MensajeHandler = Callable[[dict], Awaitable[None]]


class RabbitMQConsumer:
    """Se suscribe a un exchange topic de RabbitMQ y despacha cada mensaje
    (ya deserializado) al handler dado. Corre como tarea de fondo dentro del
    lifespan de la aplicacion."""

    def __init__(self, rabbitmq_url: str, exchange_name: str, queue_name: str, routing_key: str):
        self._url = rabbitmq_url
        self._exchange_name = exchange_name
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._tarea: asyncio.Task | None = None

    async def iniciar(self, handler: MensajeHandler) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange(
            self._exchange_name, ExchangeType.TOPIC, durable=True
        )
        queue = await channel.declare_queue(self._queue_name, durable=True)
        await queue.bind(exchange, routing_key=self._routing_key)

        self._tarea = asyncio.create_task(self._consumir(queue, handler))
        logger.info(
            "rabbitmq_consumer_iniciado", queue=self._queue_name, routing_key=self._routing_key
        )

    async def _consumir(self, queue: aio_pika.abc.AbstractQueue, handler: MensajeHandler) -> None:
        async with queue.iterator() as queue_iter:
            async for mensaje in queue_iter:
                async with mensaje.process(ignore_processed=True):
                    try:
                        payload = json.loads(mensaje.body.decode("utf-8"))
                        await handler(payload)
                    except Exception:
                        logger.error(
                            "error_procesando_mensaje",
                            routing_key=mensaje.routing_key,
                            exc_info=True,
                        )

    async def detener(self) -> None:
        if self._tarea is not None:
            self._tarea.cancel()
        if self._connection is not None:
            await self._connection.close()
        logger.info("rabbitmq_consumer_detenido")

    @property
    def esta_conectado(self) -> bool:
        return self._connection is not None and not self._connection.is_closed
