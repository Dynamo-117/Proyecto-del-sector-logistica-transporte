import asyncio
import json
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.api.dependencies import Broadcaster

router = APIRouter(prefix="/vehiculos", tags=["tiempo-real"])

INTERVALO_KEEPALIVE_SEGUNDOS = 15


@router.get(
    "/{vehiculo_id}/eventos",
    summary="Stream en tiempo real (SSE) de telemetria de un vehiculo",
    description=(
        "Server-Sent Events: cada vez que llega un nuevo punto de telemetria "
        "para este vehiculo, se envia como evento 'data: <json>'."
    ),
)
async def stream_telemetria(
    vehiculo_id: UUID, request: Request, broadcaster: Broadcaster
) -> StreamingResponse:
    async def generador_eventos():
        async with broadcaster.suscribirse(vehiculo_id) as cola:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(
                        cola.get(), timeout=INTERVALO_KEEPALIVE_SEGUNDOS
                    )
                    yield f"data: {json.dumps(payload)}\n\n"
                except TimeoutError:
                    yield ": keep-alive\n\n"

    return StreamingResponse(generador_eventos(), media_type="text/event-stream")
