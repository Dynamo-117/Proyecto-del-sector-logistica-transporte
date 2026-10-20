import pytest

from app.infrastructure.messaging.publicador_proxy import PublicadorEventosProxy


class BrokerFalso:
    """Sujeto Real simulado: puede estar caido y recordar lo que recibe."""

    def __init__(self, disponible: bool = True):
        self.disponible = disponible
        self._conectado = False
        self.intentos_de_conexion = 0
        self.recibidos: list[tuple[str, dict]] = []

    @property
    def esta_conectado(self) -> bool:
        return self._conectado

    async def conectar(self) -> None:
        self.intentos_de_conexion += 1
        if not self.disponible:
            raise ConnectionError("broker caido")
        self._conectado = True

    async def desconectar(self) -> None:
        self._conectado = False

    async def publicar(self, routing_key: str, payload: dict) -> None:
        if not self._conectado:
            raise RuntimeError("no conectado")
        self.recibidos.append((routing_key, payload))


class Reloj:
    def __init__(self):
        self.ahora = 0.0

    def __call__(self) -> float:
        return self.ahora


async def test_con_el_broker_disponible_el_proxy_entrega_directamente():
    broker = BrokerFalso()
    proxy = PublicadorEventosProxy(broker)
    await proxy.conectar()

    await proxy.publicar("vehiculo.creado", {"id": 1})

    assert broker.recibidos == [("vehiculo.creado", {"id": 1})]
    assert (proxy.publicados, proxy.pendientes) == (1, 0)


async def test_si_el_broker_esta_caido_al_iniciar_el_servicio_arranca_igual():
    proxy = PublicadorEventosProxy(BrokerFalso(disponible=False))

    await proxy.conectar()

    assert not proxy.esta_conectado


async def test_con_el_broker_caido_la_operacion_no_falla_y_el_evento_queda_pendiente():
    proxy = PublicadorEventosProxy(BrokerFalso(disponible=False))
    await proxy.conectar()

    await proxy.publicar("vehiculo.creado", {"id": 1})
    await proxy.publicar("vehiculo.actualizado", {"id": 1})

    assert proxy.pendientes == 2
    assert proxy.publicados == 0


async def test_al_volver_el_broker_entrega_los_pendientes_en_el_mismo_orden():
    broker = BrokerFalso(disponible=False)
    reloj = Reloj()
    proxy = PublicadorEventosProxy(broker, espera_reintento_s=5, reloj=reloj)
    await proxy.conectar()
    await proxy.publicar("a", {"n": 1})
    await proxy.publicar("b", {"n": 2})

    broker.disponible = True
    entregados = await proxy.entregar_pendientes(forzar=True)
    await proxy.publicar("c", {"n": 3})

    assert entregados == 2
    assert [k for k, _ in broker.recibidos] == ["a", "b", "c"]
    assert proxy.pendientes == 0 and proxy.esta_conectado


async def test_no_satura_al_broker_con_reintentos_de_conexion():
    broker = BrokerFalso(disponible=False)
    reloj = Reloj()
    proxy = PublicadorEventosProxy(broker, espera_reintento_s=5, reloj=reloj)
    await proxy.conectar()
    intentos_iniciales = broker.intentos_de_conexion

    for _ in range(10):
        await proxy.publicar("x", {})
    assert broker.intentos_de_conexion == intentos_iniciales

    reloj.ahora = 6
    await proxy.publicar("x", {})
    assert broker.intentos_de_conexion == intentos_iniciales + 1


async def test_el_buzon_esta_acotado_y_descarta_los_mas_viejos():
    proxy = PublicadorEventosProxy(BrokerFalso(disponible=False), capacidad_pendientes=3)
    await proxy.conectar()

    for i in range(5):
        await proxy.publicar("x", {"n": i})

    assert proxy.pendientes == 3
    assert proxy.descartados == 2


async def test_un_fallo_al_publicar_deja_el_evento_pendiente_sin_propagar_el_error():
    class BrokerQueFallaAlPublicar(BrokerFalso):
        async def publicar(self, routing_key, payload):
            raise RuntimeError("canal cerrado")

    proxy = PublicadorEventosProxy(BrokerQueFallaAlPublicar())
    await proxy.conectar()

    await proxy.publicar("x", {})

    assert proxy.pendientes == 1 and proxy.publicados == 0


async def test_desconectar_se_delega_en_el_sujeto_real():
    broker = BrokerFalso()
    proxy = PublicadorEventosProxy(broker)
    await proxy.conectar()

    await proxy.desconectar()

    assert not proxy.esta_conectado


@pytest.mark.parametrize("metodo", ["publicar", "esta_conectado"])
def test_el_proxy_ofrece_la_misma_interfaz_que_el_publicador(metodo):
    assert hasattr(PublicadorEventosProxy, metodo)
