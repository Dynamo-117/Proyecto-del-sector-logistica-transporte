from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_exception_handlers
from app.api.middleware import CorrelationIdMiddleware
from app.api.routes.asignacion_routes import router as asignacion_router
from app.api.routes.grafo_routes import router as grafo_router
from app.api.routes.health_routes import router as health_router
from app.application.use_cases.vehiculo_use_cases import (
    ActualizarEstadoVehiculoPorAsignacionConductor,
    SincronizarVehiculoDisponible,
)
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.domain.entities import EstadoVehiculo
from app.infrastructure.db.session import async_session_factory
from app.infrastructure.db.vehiculo_disponible_repository import (
    SqlAlchemyVehiculoDisponibleRepository,
)
from app.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


async def _manejar_evento_vehiculo(routing_key: str, payload: dict) -> None:
    async with async_session_factory() as session:
        repo = SqlAlchemyVehiculoDisponibleRepository(session)

        if routing_key in ("vehiculo.creado", "vehiculo.actualizado"):
            await SincronizarVehiculoDisponible(repo).ejecutar(
                UUID(payload["id"]), payload["placa"], payload["capacidad_kg"], payload["estado"]
            )
        elif routing_key == "vehiculo.conductor_asignado":
            await ActualizarEstadoVehiculoPorAsignacionConductor(repo).ejecutar(
                UUID(payload["vehiculo_id"]), EstadoVehiculo.EN_RUTA
            )
        elif routing_key == "vehiculo.conductor_desasignado":
            await ActualizarEstadoVehiculoPorAsignacionConductor(repo).ejecutar(
                UUID(payload["vehiculo_id"]), EstadoVehiculo.DISPONIBLE
            )
        else:
            logger.warning("routing_key_no_reconocida", routing_key=routing_key)

    logger.info("evento_vehiculo_procesado", routing_key=routing_key)


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
        title="Route Optimization Service",
        description="Calculo de rutas (Dijkstra) y asignacion de cargas a vehiculos disponibles.",
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
    app.include_router(grafo_router)
    app.include_router(asignacion_router)

    return app


app = create_app()
