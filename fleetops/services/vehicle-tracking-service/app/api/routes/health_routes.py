from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.infrastructure.db.session import async_session_factory

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", summary="Readiness probe")
async def ready(request: Request) -> JSONResponse:
    checks = {"database": False, "rabbitmq": False}

    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False

    consumer = getattr(request.app.state, "rabbitmq_consumer", None)
    checks["rabbitmq"] = bool(consumer and consumer.esta_conectado)

    all_ok = all(checks.values())
    return JSONResponse(
        status_code=status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
    )
