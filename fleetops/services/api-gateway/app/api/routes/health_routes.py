import httpx
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings

router = APIRouter(tags=["health"])

TIMEOUT_CHEQUEO_SEGUNDOS = 3.0


@router.get("/health", summary="Liveness probe")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Verifica que cada microservicio registrado responda en su propio /health.",
)
async def ready(request: Request) -> JSONResponse:
    client: httpx.AsyncClient = request.app.state.http_client
    settings = get_settings()

    checks: dict[str, bool] = {}
    for nombre, base_url in settings.rutas_servicios.items():
        try:
            respuesta = await client.get(f"{base_url}/health", timeout=TIMEOUT_CHEQUEO_SEGUNDOS)
            checks[nombre] = respuesta.status_code == 200
        except httpx.HTTPError:
            checks[nombre] = False

    all_ok = all(checks.values())
    return JSONResponse(
        status_code=status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
    )
