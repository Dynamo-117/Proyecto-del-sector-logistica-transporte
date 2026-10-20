from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from uuid import UUID

from app.application.reportes.formato_reporte import FormatoReporte
from app.domain.entities import Conductor, EstadoVehiculo, Vehiculo


@dataclass(frozen=True)
class ReporteGenerado:
    contenido: str
    media_type: str
    nombre_archivo: str


class Reporte(ABC):
    # =================   PATRON GOF: BRIDGE (Abstraccion) -- inicia aqui =================
    """La Abstraccion: la jerarquia "que reporte se quiere". Guarda una
    referencia al Implementador (el "puente") y le delega la escritura. Cada
    Abstraccion refinada (ReporteVehiculos, ReporteConductores, ...) solo decide
    QUE datos van en el reporte; el COMO se escribe lo decide el formato que
    reciba. Asi las dos jerarquias crecen por separado: N reportes + M formatos
    en lugar de N x M clases.
    """

    nombre: str

    def __init__(self, formato: FormatoReporte):
        self._formato = formato

    @abstractmethod
    def titulo(self) -> str: ...

    @abstractmethod
    def columnas(self) -> list[str]: ...

    @abstractmethod
    def filas(self) -> list[list[str]]: ...

    def generar(self) -> ReporteGenerado:
        contenido = self._formato.render(self.titulo(), self.columnas(), self.filas())
        return ReporteGenerado(
            contenido=contenido,
            media_type=self._formato.media_type,
            nombre_archivo=f"{self.nombre}.{self._formato.extension}",
        )


class ReporteVehiculos(Reporte):
    nombre = "vehiculos"

    def __init__(
        self,
        formato: FormatoReporte,
        vehiculos: list[Vehiculo],
        nombres_conductores: Mapping[UUID, str],
    ):
        super().__init__(formato)
        self._vehiculos = vehiculos
        self._nombres = nombres_conductores

    def titulo(self) -> str:
        return "Reporte de vehiculos"

    def columnas(self) -> list[str]:
        return ["Placa", "Tipo", "Capacidad (kg)", "Estado", "Conductor"]

    def filas(self) -> list[list[str]]:
        return [
            [
                v.placa,
                v.tipo.value,
                f"{v.capacidad_kg:g}",
                v.estado.value,
                (
                    self._nombres.get(v.conductor_id, "Sin asignar")
                    if v.conductor_id
                    else "Sin asignar"
                ),
            ]
            for v in self._vehiculos
        ]


class ReporteConductores(Reporte):
    nombre = "conductores"

    def __init__(self, formato: FormatoReporte, conductores: list[Conductor]):
        super().__init__(formato)
        self._conductores = conductores

    def titulo(self) -> str:
        return "Reporte de conductores"

    def columnas(self) -> list[str]:
        return ["Nombre", "Licencia", "Estado"]

    def filas(self) -> list[list[str]]:
        return [[c.nombre, c.licencia, c.estado.value] for c in self._conductores]


class ReporteResumenFlota(Reporte):
    nombre = "resumen"

    def __init__(self, formato: FormatoReporte, vehiculos: list[Vehiculo]):
        super().__init__(formato)
        self._vehiculos = vehiculos

    def titulo(self) -> str:
        return "Resumen de la flota por estado"

    def columnas(self) -> list[str]:
        return ["Estado", "Vehiculos", "Capacidad total (kg)"]

    def filas(self) -> list[list[str]]:
        cantidad: Counter[EstadoVehiculo] = Counter()
        capacidad: Counter[EstadoVehiculo] = Counter()
        for v in self._vehiculos:
            cantidad[v.estado] += 1
            capacidad[v.estado] += v.capacidad_kg
        return [[e.value, str(cantidad[e]), f"{capacidad[e]:g}"] for e in EstadoVehiculo]

    # ================= PATRON GOF: BRIDGE (Abstraccion) -- termina aqui =================
