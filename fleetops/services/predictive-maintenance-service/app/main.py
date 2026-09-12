from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_exception_handlers
from app.api.middleware import CorrelationIdMiddleware
from app.api.routes.alerta_routes import router as alerta_router
from app.api.routes.health_routes import router as health_router
from app.api.routes.lectura_routes import router as lectura_router
from app.application.use_cases.vehiculo_use_cases import SincronizarVehiculoConocido
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.db.session import async_session_factory
from app.infrastructure.db.vehiculo_repository import SqlAlchemyVehiculoConocidoRepository
from app.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


async def _manejar_evento_vehiculo(routing_key: str, payload: dict) -> None:
    if routing_key not in ("vehiculo.creado", "vehiculo.actualizado"):
        return

    async with async_session_factory() as session:
        repo = SqlAlchemyVehiculoConocidoRepository(session)
        await SincronizarVehiculoConocido(repo).ejecutar(UUID(payload["id"]), payload["placa"])

    logger.info("vehiculo_conocido_sincronizado", vehiculo_id=payload["id"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = RabbitMQConsumer(
        settings.rabbitmq_url,
        settings.rabbitmq_exchange,
        settings.rabbitmq_queue,
        settings.rabbitmq_routing_key,
    )
    await consumer.iniciar(_manejar_evento_vehiculo)
    app.state.rabbitmq_consumer = consumer

    logger.info("servicio_iniciado", app=settings.app_name)
    yield

    await consumer.detener()
    logger.info("servicio_detenido", app=settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Predictive Maintenance Service",
        description="Alertas de mantenimiento por umbrales de kilometraje y horas de motor.",
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
    app.include_router(lectura_router)
    app.include_router(alerta_router)

    return app


app = create_app()
