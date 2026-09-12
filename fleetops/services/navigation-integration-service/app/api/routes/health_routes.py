from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/ready",
    summary="Readiness probe",
    description=(
        "Este servicio no tiene base de datos ni broker propios: solo depende del "
        "proveedor externo de rutas, que se consulta bajo demanda en /rutas/calcular "
        "y no aqui, para no saturar el servidor publico de OSRM con cada chequeo."
    ),
)
async def ready() -> dict[str, str]:
    return {"status": "ok"}
