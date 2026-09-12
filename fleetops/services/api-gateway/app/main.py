from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_exception_handlers
from app.api.middleware import CorrelationIdMiddleware, JWTAuthMiddleware
from app.api.routes.health_routes import router as health_router
from app.api.routes.proxy_routes import router as proxy_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.external.httpx_proxy_client import HttpxProxyClient

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = httpx.AsyncClient(timeout=settings.proxy_timeout_segundos)
    app.state.http_client = http_client
    app.state.proxy_client = HttpxProxyClient(http_client)

    logger.info("servicio_iniciado", app=settings.app_name, rutas=settings.rutas_servicios)
    yield

    await http_client.aclose()
    logger.info("servicio_detenido", app=settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title="API Gateway",
        description="Punto de entrada unico de FleetOps: enruta al microservicio correspondiente.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Orden de add_middleware (el ultimo agregado queda mas afuera): JWT valida
    # primero la peticion ya dentro del stack, Correlation la envuelve para que
    # sus respuestas de error tambien lleven x-correlation-id, y CORS queda
    # completamente afuera para resolver preflights (OPTIONS) sin pasar por auth.
    app.add_middleware(
        JWTAuthMiddleware, secret_key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm
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

    # Orden importa: /health y /ready deben registrarse antes que el catch-all
    # del proxy, que si no las capturaria como si "health"/"ready" fueran el
    # prefijo de un microservicio.
    app.include_router(health_router)
    app.include_router(proxy_router)

    return app


app = create_app()
