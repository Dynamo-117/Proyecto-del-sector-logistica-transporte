from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_exception_handlers
from app.api.middleware import CorrelationIdMiddleware
from app.api.routes.health_routes import router as health_router
from app.api.routes.stream_routes import router as stream_router
from app.api.routes.telemetria_routes import router as telemetria_router
from app.api.routes.vehiculo_routes import router as vehiculo_router
from app.application.use_cases.vehiculo_use_cases import RegistrarVehiculoConocido
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.db.session import async_session_factory
from app.infrastructure.db.vehiculo_conocido_repository import SqlAlchemyVehiculoConocidoRepository
from app.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from app.infrastructure.realtime.in_memory_broadcaster import InMemoryBroadcaster

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


async def _manejar_vehiculo_creado(payload: dict) -> None:
    async with async_session_factory() as session:
        repo = SqlAlchemyVehiculoConocidoRepository(session)
        await RegistrarVehiculoConocido(repo).ejecutar(UUID(payload["id"]), payload["placa"])
    logger.info("vehiculo_conocido_registrado", vehiculo_id=payload["id"], placa=payload["placa"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.broadcaster = InMemoryBroadcaster()

    consumer = RabbitMQConsumer(
        settings.rabbitmq_url,
        settings.rabbitmq_exchange,
        settings.rabbitmq_queue,
        settings.rabbitmq_routing_key,
    )
    await consumer.iniciar(_manejar_vehiculo_creado)
    app.state.rabbitmq_consumer = consumer

    logger.info("servicio_iniciado", app=settings.app_name)
    yield

    await consumer.detener()
    logger.info("servicio_detenido", app=settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Vehicle Tracking Service",
        description="Ingestion de telemetria y estado en tiempo real de la flota FleetOps.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(telemetria_router)
    app.include_router(vehiculo_router)
    app.include_router(stream_router)

    return app


app = create_app()
