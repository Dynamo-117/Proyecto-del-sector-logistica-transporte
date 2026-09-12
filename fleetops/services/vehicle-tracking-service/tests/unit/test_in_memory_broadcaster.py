import asyncio
from uuid import uuid4

from app.infrastructure.realtime.in_memory_broadcaster import InMemoryBroadcaster


async def test_suscriptor_recibe_payload_publicado():
    broadcaster = InMemoryBroadcaster()
    vehiculo_id = uuid4()

    async with broadcaster.suscribirse(vehiculo_id) as cola:
        await broadcaster.publicar(vehiculo_id, {"velocidad_kmh": 42})
        payload = await asyncio.wait_for(cola.get(), timeout=1)

    assert payload == {"velocidad_kmh": 42}


async def test_publicar_sin_suscriptores_no_falla():
    broadcaster = InMemoryBroadcaster()
    await broadcaster.publicar(uuid4(), {"velocidad_kmh": 1})


async def test_suscriptor_no_recibe_eventos_de_otro_vehiculo():
    broadcaster = InMemoryBroadcaster()
    vehiculo_a, vehiculo_b = uuid4(), uuid4()

    async with broadcaster.suscribirse(vehiculo_a) as cola:
        await broadcaster.publicar(vehiculo_b, {"velocidad_kmh": 99})
        assert cola.empty()


async def test_al_salir_del_context_manager_se_desregistra():
    broadcaster = InMemoryBroadcaster()
    vehiculo_id = uuid4()

    async with broadcaster.suscribirse(vehiculo_id):
        assert len(broadcaster._suscriptores[vehiculo_id]) == 1

    assert len(broadcaster._suscriptores[vehiculo_id]) == 0
