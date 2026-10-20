"""Demostracion del patron BRIDGE en fleet-management-service.

Dos jerarquias independientes (que reporte / como se escribe) unidas por un
"puente": cada reporte recibe un formato. 3 reportes x 3 formatos = 9
combinaciones con solo 6 clases. Al final se agrega un formato nuevo (Markdown)
sin modificar ningun reporte.

Uso (desde services/fleet-management-service, con el entorno virtual activo):
    python -m scripts.demo_bridge
"""

from app.application.reportes.formato_reporte import FormatoReporte
from app.application.reportes.reporte import (
    ReporteConductores,
    ReporteResumenFlota,
    ReporteVehiculos,
)
from app.domain.entities import Conductor, EstadoVehiculo, TipoVehiculo, Vehiculo
from app.infrastructure.reportes.formatos import FORMATOS

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


class FormatoMarkdown(FormatoReporte):
    """Formato nuevo, definido solo para esta demostracion."""

    media_type = "text/markdown"
    extension = "md"

    def render(self, titulo: str, columnas: list[str], filas: list[list[str]]) -> str:
        lineas = [f"## {titulo}", "", "| " + " | ".join(columnas) + " |"]
        lineas.append("|" + "---|" * len(columnas))
        lineas += ["| " + " | ".join(fila) + " |" for fila in filas]
        return "\n".join(lineas)


def reportes(formato: FormatoReporte):
    return [
        ReporteVehiculos(formato, VEHICULOS, {CAMILA.id: CAMILA.nombre}),
        ReporteConductores(formato, [CAMILA]),
        ReporteResumenFlota(formato, VEHICULOS),
    ]


def main() -> None:
    print("PATRON BRIDGE -- fleet-management-service\n")

    print("1) Matriz de combinaciones: cada Abstraccion (reporte) x cada Implementador (formato)")
    print(f"   {'ABSTRACCION':<24}{'FORMATO':<16}{'ARCHIVO GENERADO':<22}{'BYTES':>6}")
    print("   " + "-" * 68)
    for formato in FORMATOS.values():
        for reporte in reportes(formato):
            generado = reporte.generar()
            print(
                f"   {type(reporte).__name__:<24}{type(formato).__name__:<16}"
                f"{generado.nombre_archivo:<22}{len(generado.contenido):>6}"
            )
    print("   -> 9 combinaciones con 3 abstracciones + 3 implementadores = 6 clases\n")

    print("2) Misma abstraccion (ReporteVehiculos), tres formatos distintos:")
    for nombre in ("csv", "json", "html"):
        generado = ReporteVehiculos(
            FORMATOS[nombre], VEHICULOS, {CAMILA.id: CAMILA.nombre}
        ).generar()
        primeras = generado.contenido.lstrip("﻿").splitlines()[:3]
        print(f"   [{generado.nombre_archivo}] {generado.media_type}")
        for linea in primeras:
            print(f"      {linea[:96]}")
    print()

    print("3) Formato NUEVO (Markdown) con los tres reportes, sin tocar ningun reporte:")
    for reporte in reportes(FormatoMarkdown()):
        generado = reporte.generar()
        print(f"   [{generado.nombre_archivo}]")
        for linea in generado.contenido.splitlines():
            print(f"      {linea}")

    print("\nRESULTADO: reportes y formatos evolucionan por separado, unidos por el puente.")


if __name__ == "__main__":
    main()
