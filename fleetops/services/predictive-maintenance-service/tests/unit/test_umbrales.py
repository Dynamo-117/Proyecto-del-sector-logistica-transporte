from uuid import uuid4

from app.domain.entities import EstadoMantenimiento, TipoAlerta, evaluar_tipos_a_alertar


def test_sin_desgaste_no_genera_alertas():
    tipos = evaluar_tipos_a_alertar(kilometraje_actual=100, horas_actual=10, estados_actuales={})

    assert tipos == []


def test_supera_umbral_de_cambio_de_aceite_por_kilometraje():
    tipos = evaluar_tipos_a_alertar(kilometraje_actual=10_000, horas_actual=0, estados_actuales={})

    assert TipoAlerta.CAMBIO_ACEITE in tipos
    assert TipoAlerta.REVISION_GENERAL not in tipos


def test_supera_umbral_de_revision_general_por_horas():
    tipos = evaluar_tipos_a_alertar(kilometraje_actual=0, horas_actual=600, estados_actuales={})

    assert TipoAlerta.REVISION_GENERAL in tipos


def test_umbral_se_cuenta_desde_la_base_del_ultimo_mantenimiento():
    vehiculo_id = uuid4()
    estados = {
        TipoAlerta.CAMBIO_ACEITE: EstadoMantenimiento(
            vehiculo_id=vehiculo_id, tipo=TipoAlerta.CAMBIO_ACEITE, km_base=50_000, horas_base=0
        )
    }

    tipos = evaluar_tipos_a_alertar(
        kilometraje_actual=55_000, horas_actual=0, estados_actuales=estados
    )

    assert TipoAlerta.CAMBIO_ACEITE not in tipos

    tipos = evaluar_tipos_a_alertar(
        kilometraje_actual=60_000, horas_actual=0, estados_actuales=estados
    )

    assert TipoAlerta.CAMBIO_ACEITE in tipos
