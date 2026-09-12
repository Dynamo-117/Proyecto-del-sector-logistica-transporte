from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_exception_handlers
from app.api.middleware import CorrelationIdMiddleware
from app.api.routes.health_routes import router as health_router
from app.api.routes.ruta_routes import router as ruta_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.external.osrm_client import OSRMClient

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    provider = OSRMClient(settings.osrm_base_url, timeout=settings.osrm_timeout_segundos)
    app.state.navigation_provider = provider

    logger.info("servicio_iniciado", app=settings.app_name, osrm_base_url=settings.osrm_base_url)
    yield

    await provider.cerrar()
    logger.info("servicio_detenido", app=settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Navigation Integration Service",
        description="Interfaz propia y normalizada sobre un proveedor externo de navegacion.",
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
    app.include_router(ruta_router)

    return app


app = create_app()
