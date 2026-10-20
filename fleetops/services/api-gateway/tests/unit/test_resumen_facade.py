import pytest

from app.application.facade.resumen_operativo_facade import ResumenOperativoFacade
from app.domain.exceptions import ServicioNoDisponible

V1, V2, V3 = "id-1", "id-2", "id-3"


class FlotaFalsa:
    def __init__(self, caida=False):
        self._caida = caida

    async def listar_vehiculos(self, headers):
        if self._caida:
            raise ServicioNoDisponible("flota caida")
        return [
            {"id": V1, "estado": "DISPONIBLE"},
            {"id": V2, "estado": "EN_RUTA"},
            {"id": V3, "estado": "EN_RUTA"},
        ]

    async def listar_conductores(self, headers):
        return [{"estado": "DISPONIBLE"}, {"estado": "ASIGNADO"}]


class RutasFalsas:
    def __init__(self, caida=False):
        self._caida = caida

    async def listar_rutas_activas(self, headers):
        if self._caida:
            raise ServicioNoDisponible("rutas caido")
        return [{"distancia_km": 415.0}, {"distancia_km": 100.5}]


class MantenimientoFalso:
    def __init__(self, caida=False):
        self._caida = caida
        self.llamadas = []

    async def contar_alertas_activas(self, vehiculo_id, headers):
        self.llamadas.append(vehiculo_id)
        if self._caida:
            raise ServicioNoDisponible("mantenimiento caido")
        return {V1: 2, V2: 0, V3: 1}[vehiculo_id]


class TrackingFalso:
    async def estado_movimiento(self, vehiculo_id, headers):
        return {V1: "EN_MOVIMIENTO", V2: "DETENIDO", V3: None}[vehiculo_id]


def _fachada(**kw):
    return ResumenOperativoFacade(
        flota=FlotaFalsa(kw.get("flota_caida", False)),
        rutas=RutasFalsas(kw.get("rutas_caido", False)),
        mantenimiento=MantenimientoFalso(kw.get("mantenimiento_caido", False)),
        tracking=TrackingFalso(),
    )


async def test_una_sola_llamada_arma_el_resumen_de_los_cuatro_subsistemas():
    resumen = await _fachada().obtener({})

    assert resumen.flota.total_vehiculos == 3
    assert resumen.flota.vehiculos_por_estado == {"DISPONIBLE": 1, "EN_RUTA": 2}
    assert resumen.flota.total_conductores == 2
    assert resumen.flota.conductores_disponibles == 1
    assert resumen.rutas.rutas_activas == 2
    assert resumen.rutas.distancia_total_km == 515.5
    assert resumen.mantenimiento.alertas_activas == 3
    assert resumen.mantenimiento.vehiculos_con_alertas == 2
    assert (resumen.tracking.en_movimiento, resumen.tracking.detenidos) == (1, 1)
    assert resumen.tracking.sin_telemetria == 1
    assert all(
        s.disponible
        for s in (resumen.flota, resumen.rutas, resumen.mantenimiento, resumen.tracking)
    )


async def test_cuenta_las_llamadas_internas_que_esconde():
    resumen = await _fachada().obtener({})

    # 2 de flota + 1 de rutas + (1 mantenimiento + 1 tracking) por vehiculo
    assert resumen.llamadas_internas == 3 + 2 * 3


async def test_un_servicio_caido_no_tumba_el_resumen_completo():
    resumen = await _fachada(rutas_caido=True).obtener({})

    assert not resumen.rutas.disponible
    assert (
        resumen.flota.disponible
        and resumen.mantenimiento.disponible
        and resumen.tracking.disponible
    )


async def test_si_mantenimiento_cae_solo_esa_seccion_queda_no_disponible():
    resumen = await _fachada(mantenimiento_caido=True).obtener({})

    assert not resumen.mantenimiento.disponible
    assert resumen.flota.disponible and resumen.tracking.disponible


async def test_sin_flota_no_se_consulta_por_vehiculo_y_dependientes_quedan_no_disponibles():
    fachada = _fachada(flota_caida=True)

    resumen = await fachada.obtener({})

    assert not resumen.flota.disponible
    assert not resumen.mantenimiento.disponible and not resumen.tracking.disponible
    assert resumen.rutas.disponible
    assert fachada._mantenimiento.llamadas == []


async def test_reenvia_los_headers_a_los_subsistemas():
    recibidos = []

    class FlotaEspia(FlotaFalsa):
        async def listar_vehiculos(self, headers):
            recibidos.append(headers)
            return []

    fachada = ResumenOperativoFacade(
        FlotaEspia(), RutasFalsas(), MantenimientoFalso(), TrackingFalso()
    )

    resumen = await fachada.obtener({"authorization": "Bearer abc"})

    assert recibidos == [{"authorization": "Bearer abc"}]
    assert resumen.flota.total_vehiculos == 0 and resumen.mantenimiento.alertas_activas == 0


@pytest.mark.parametrize("campo", ["flota", "rutas", "mantenimiento", "tracking"])
async def test_el_resumen_expone_las_cuatro_secciones(campo):
    resumen = await _fachada().obtener({})

    assert hasattr(resumen, campo)
