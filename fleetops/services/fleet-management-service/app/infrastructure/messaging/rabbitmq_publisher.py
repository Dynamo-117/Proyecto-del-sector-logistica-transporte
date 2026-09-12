from __future__ import annotations

import json
from typing import Any

import aio_pika
from aio_pika import ExchangeType

from app.core.logging import get_logger

logger = get_logger(__name__)


class RabbitMQPublisher:
    """Publicador de eventos de dominio sobre un exchange topic de RabbitMQ."""

    def __init__(self, rabbitmq_url: str, exchange_name: str):
        self._url = rabbitmq_url
        self._exchange_name = exchange_name
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def conectar(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            self._exchange_name, ExchangeType.TOPIC, durable=True
        )
        logger.info("rabbitmq_conectado", exchange=self._exchange_name)

    @property
    def esta_conectado(self) -> bool:
        return self._connection is not None and not self._connection.is_closed

    async def desconectar(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            logger.info("rabbitmq_desconectado")

    async def publicar(self, routing_key: str, payload: dict[str, Any]) -> None:
        if self._exchange is None:
            raise RuntimeError("RabbitMQPublisher no esta conectado; llama a conectar() primero")

        mensaje = aio_pika.Message(
            body=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await self._exchange.publish(mensaje, routing_key=routing_key)
        logger.info("evento_publicado", routing_key=routing_key)
