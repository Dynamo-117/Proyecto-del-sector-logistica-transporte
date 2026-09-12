from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_exception_handlers
from app.api.middleware import CorrelationIdMiddleware
from app.api.routes.asignacion_routes import router as asignacion_router
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.conductor_routes import router as conductor_router
from app.api.routes.health_routes import router as health_router
from app.api.routes.vehiculo_routes import router as vehiculo_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    publisher = RabbitMQPublisher(settings.rabbitmq_url, settings.rabbitmq_exchange)
    await publisher.conectar()
    app.state.event_publisher = publisher

    logger.info("servicio_iniciado", app=settings.app_name)
    yield

    await publisher.desconectar()
    logger.info("servicio_detenido", app=settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Fleet Management Service",
        description="Gestion de vehiculos, conductores y su asignacion dentro de FleetOps.",
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
    app.include_router(auth_router)
    app.include_router(vehiculo_router)
    app.include_router(conductor_router)
    app.include_router(asignacion_router)

    return app


app = create_app()
