from app.infrastructure.messaging.publicador_proxy import PublicadorEventosProxy
from tests.unit.test_publicador_proxy import BrokerFalso


async def _proxy(app, disponible: bool) -> tuple[PublicadorEventosProxy, BrokerFalso]:
    broker = BrokerFalso(disponible=disponible)
    proxy = PublicadorEventosProxy(broker, espera_reintento_s=0)
    await proxy.conectar()
    app.state.event_publisher = proxy
    return proxy, broker


async def test_estado_con_el_broker_caido_muestra_los_pendientes(app, client):
    proxy, _ = await _proxy(app, disponible=False)
    await proxy.publicar("vehiculo.creado", {"id": 1})

    cuerpo = (await client.get("/eventos/estado")).json()

    assert cuerpo == {"conectado": False, "pendientes": 1, "publicados": 0, "descartados": 0}


async def test_reintentar_entrega_los_pendientes_cuando_el_broker_vuelve(app, client):
    proxy, broker = await _proxy(app, disponible=False)
    await proxy.publicar("vehiculo.creado", {"id": 1})
    broker.disponible = True

    respuesta = await client.post("/eventos/reintentar")

    assert respuesta.json() == {"entregados": 1, "pendientes": 0}
    assert (await client.get("/eventos/estado")).json()["conectado"] is True
