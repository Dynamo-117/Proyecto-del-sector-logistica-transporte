import json
from uuid import uuid4

import pytest

from app.application.reportes.formato_reporte import FormatoReporte
from app.application.reportes.reporte import (
    Reporte,
    ReporteConductores,
    ReporteResumenFlota,
    ReporteVehiculos,
)
from app.application.use_cases.reporte_use_cases import GenerarReporte
from app.domain.entities import Conductor, EstadoVehiculo, TipoVehiculo, Vehiculo
from app.domain.exceptions import ReporteNoSoportado
from app.infrastructure.reportes.formatos import FORMATOS, FormatoCSV, FormatoHTML, FormatoJSON
from tests.unit.fakes import FakeConductorRepository, FakeVehiculoRepository

CAMILA = Conductor(nombre="Camila Ruiz", licencia="LIC-4471")
VEHICULOS = [
    Vehiculo(placa="TRK001", tipo=TipoVehiculo.CAMION, capacidad_kg=800),
    Vehiculo(
        placa="VAN042",
        tipo=TipoVehiculo.VAN,
        capacidad_kg=600,
        estado=EstadoVehiculo.EN_RUTA,
        conductor_id=CAMILA.id,
    ),
]


def _reportes(formato: FormatoReporte) -> list[Reporte]:
    return [
        ReporteVehiculos(formato, VEHICULOS, {CAMILA.id: CAMILA.nombre}),
        ReporteConductores(formato, [CAMILA]),
        ReporteResumenFlota(formato, VEHICULOS),
    ]


def test_el_formato_abstracto_no_se_puede_instanciar():
    with pytest.raises(TypeError):
        FormatoReporte()


def test_la_abstraccion_no_se_puede_instanciar():
    with pytest.raises(TypeError):
        Reporte(FormatoCSV())


@pytest.mark.parametrize("formato", list(FORMATOS.values()), ids=list(FORMATOS))
def test_todo_reporte_se_escribe_en_todo_formato(formato):
    for reporte in _reportes(formato):
        generado = reporte.generar()

        assert generado.contenido
        assert generado.media_type == formato.media_type
        assert generado.nombre_archivo == f"{reporte.nombre}.{formato.extension}"


def test_csv_tiene_cabecera_y_una_fila_por_vehiculo():
    contenido = ReporteVehiculos(FormatoCSV(), VEHICULOS, {CAMILA.id: CAMILA.nombre}).generar()
    lineas = contenido.contenido.lstrip("﻿").splitlines()

    assert lineas[0] == "Placa,Tipo,Capacidad (kg),Estado,Conductor"
    assert lineas[1] == "TRK001,CAMION,800,DISPONIBLE,Sin asignar"
    assert lineas[2] == "VAN042,VAN,600,EN_RUTA,Camila Ruiz"


def test_json_expone_las_filas_como_objetos():
    contenido = ReporteConductores(FormatoJSON(), [CAMILA]).generar().contenido
    datos = json.loads(contenido)

    assert datos["total"] == 1
    assert datos["filas"][0] == {
        "Nombre": "Camila Ruiz",
        "Licencia": "LIC-4471",
        "Estado": "DISPONIBLE",
    }


def test_html_escapa_el_contenido():
    peligroso = Conductor(nombre="<script>alert(1)</script>", licencia="X")

    contenido = ReporteConductores(FormatoHTML(), [peligroso]).generar().contenido

    assert "<script>alert(1)</script>" not in contenido
    assert "&lt;script&gt;" in contenido


def test_resumen_cuenta_vehiculos_y_capacidad_por_estado():
    filas = ReporteResumenFlota(FormatoCSV(), VEHICULOS).filas()

    assert ["DISPONIBLE", "1", "800"] in filas
    assert ["EN_RUTA", "1", "600"] in filas
    assert ["MANTENIMIENTO", "0", "0"] in filas


def test_un_formato_nuevo_funciona_con_todos_los_reportes_sin_tocarlos():
    class FormatoTexto(FormatoReporte):
        media_type = "text/plain"
        extension = "txt"

        def render(self, titulo, columnas, filas):
            return "\n".join([titulo, " | ".join(columnas), *(" | ".join(f) for f in filas)])

    for reporte in _reportes(FormatoTexto()):
        generado = reporte.generar()

        assert generado.nombre_archivo.endswith(".txt")
        assert generado.contenido.startswith(reporte.titulo())


async def test_caso_de_uso_cruza_cada_tipo_con_el_formato_elegido():
    vehiculos, conductores = FakeVehiculoRepository(), FakeConductorRepository()
    for v in VEHICULOS:
        await vehiculos.crear(v)
    await conductores.crear(CAMILA)
    caso = GenerarReporte(vehiculos, conductores)

    for tipo in ("vehiculos", "conductores", "resumen"):
        for nombre, formato in FORMATOS.items():
            generado = await caso.ejecutar(tipo, formato)
            assert generado.nombre_archivo == f"{tipo}.{formato.extension}", nombre


async def test_caso_de_uso_rechaza_un_tipo_desconocido():
    caso = GenerarReporte(FakeVehiculoRepository(), FakeConductorRepository())

    with pytest.raises(ReporteNoSoportado):
        await caso.ejecutar(f"inexistente-{uuid4()}", FormatoCSV())
