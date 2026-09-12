import asyncio
import json
from uuid import uuid4

from app.api.routes.stream_routes import stream_telemetria
from app.infrastructure.realtime.in_memory_broadcaster import InMemoryBroadcaster


class _RequestSiempreConectado:
    """httpx.ASGITransport buferiza toda la respuesta antes de devolverla, por lo
    que un StreamingResponse infinito (SSE) no se puede probar de punta a punta
    con el cliente HTTP de pruebas. En su lugar se invoca la funcion de la ruta
    directamente y se lee el generador que produce."""

    async def is_disconnected(self) -> bool:
        return False


async def test_stream_telemetria_entrega_el_payload_publicado():
    broadcaster = InMemoryBroadcaster()
    vehiculo_id = uuid4()

    respuesta = await stream_telemetria(vehiculo_id, _RequestSiempreConectado(), broadcaster)

    async def publicar_pronto():
        await asyncio.sleep(0.05)
        await broadcaster.publicar(vehiculo_id, {"velocidad_kmh": 30})

    asyncio.create_task(publicar_pronto())

    primer_chunk = await asyncio.wait_for(respuesta.body_iterator.__anext__(), timeout=2)
    await respuesta.body_iterator.aclose()

    assert primer_chunk.startswith("data: ")
    assert json.loads(primer_chunk.removeprefix("data: ").strip()) == {"velocidad_kmh": 30}
