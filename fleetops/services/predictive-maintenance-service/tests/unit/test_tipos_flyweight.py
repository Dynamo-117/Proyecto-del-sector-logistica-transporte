from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from app.api.schemas.alerta_schemas import AlertaResponse
from app.domain.entities import UMBRALES_MANTENIMIENTO, Alerta, TipoAlerta
from app.domain.tipos_mantenimiento import (
    FABRICA_TIPOS,
    FabricaTiposMantenimiento,
    TipoMantenimiento,
)


def test_la_fabrica_entrega_siempre_el_mismo_objeto_para_un_tipo():
    fabrica = FabricaTiposMantenimiento()

    primero = fabrica.obtener(TipoAlerta.CAMBIO_ACEITE)
    segundo = fabrica.obtener(TipoAlerta.CAMBIO_ACEITE)

    assert primero is segundo


def test_cada_tipo_tiene_su_propio_peso_ligero():
    fabrica = FabricaTiposMantenimiento()

    aceite = fabrica.obtener(TipoAlerta.CAMBIO_ACEITE)
    general = fabrica.obtener(TipoAlerta.REVISION_GENERAL)

    assert aceite is not general
    assert aceite.nombre != general.nombre
    assert fabrica.cantidad_creada == 2


def test_la_fabrica_crea_el_objeto_solo_la_primera_vez():
    fabrica = FabricaTiposMantenimiento()
    assert fabrica.cantidad_creada == 0

    for _ in range(1000):
        fabrica.obtener(TipoAlerta.CAMBIO_ACEITE)

    assert fabrica.cantidad_creada == 1


def test_el_peso_ligero_es_inmutable_para_poder_compartirse_sin_riesgo():
    tipo = FabricaTiposMantenimiento().obtener(TipoAlerta.CAMBIO_ACEITE)

    with pytest.raises(FrozenInstanceError):
        tipo.nombre = "otro"  # type: ignore[misc]


@pytest.mark.parametrize("tipo", list(TipoAlerta))
def test_todo_tipo_de_alerta_tiene_su_peso_ligero_completo(tipo):
    peso = FabricaTiposMantenimiento().obtener(tipo)

    assert isinstance(peso, TipoMantenimiento)
    assert peso.tipo is tipo
    assert peso.nombre and peso.descripcion and peso.recomendacion
    assert peso.prioridad in {"BAJA", "MEDIA", "ALTA"}


def test_los_umbrales_del_peso_ligero_coinciden_con_los_del_dominio():
    for tipo, umbral in UMBRALES_MANTENIMIENTO.items():
        peso = FabricaTiposMantenimiento().obtener(tipo)

        assert (peso.intervalo_km, peso.intervalo_horas) == (
            umbral.intervalo_km,
            umbral.intervalo_horas,
        )


def test_miles_de_alertas_comparten_solo_un_objeto_por_tipo():
    fabrica = FabricaTiposMantenimiento()
    alertas = [
        Alerta(
            vehiculo_id=uuid4(),
            tipo=TipoAlerta.CAMBIO_ACEITE if i % 3 else TipoAlerta.REVISION_GENERAL,
            kilometraje_km=10_000 + i,
            horas_motor=300 + i,
        )
        for i in range(5000)
    ]

    pesos = [fabrica.obtener(a.tipo) for a in alertas]

    assert len({id(p) for p in pesos}) == 2
    assert fabrica.cantidad_creada == 2


def test_la_respuesta_de_la_api_trae_el_estado_compartido_del_tipo():
    alerta = Alerta(
        vehiculo_id=uuid4(),
        tipo=TipoAlerta.REVISION_GENERAL,
        kilometraje_km=20_000,
        horas_motor=600,
    )

    respuesta = AlertaResponse.desde_alerta(alerta)

    assert respuesta.tipo_info.nombre == "Revision general"
    assert respuesta.tipo_info.prioridad == "ALTA"
    assert respuesta.tipo_info.intervalo_km == 20_000
    assert FABRICA_TIPOS.obtener(TipoAlerta.REVISION_GENERAL).nombre == respuesta.tipo_info.nombre
