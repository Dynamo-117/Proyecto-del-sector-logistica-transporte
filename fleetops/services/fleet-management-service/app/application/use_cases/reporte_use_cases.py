from __future__ import annotations

from app.application.ports.repositories import ConductorRepository, VehiculoRepository
from app.application.reportes.formato_reporte import FormatoReporte
from app.application.reportes.reporte import (
    Reporte,
    ReporteConductores,
    ReporteGenerado,
    ReporteResumenFlota,
    ReporteVehiculos,
)
from app.domain.exceptions import ReporteNoSoportado

_LIMITE = 100_000


class GenerarReporte:
    """Elige la Abstraccion segun el tipo pedido y le inyecta el Implementador
    (formato) elegido: el punto donde se cruzan las dos jerarquias del Bridge."""

    def __init__(self, vehiculo_repo: VehiculoRepository, conductor_repo: ConductorRepository):
        self._vehiculos = vehiculo_repo
        self._conductores = conductor_repo

    async def ejecutar(self, tipo: str, formato: FormatoReporte) -> ReporteGenerado:
        reporte: Reporte
        if tipo == "vehiculos":
            vehiculos = await self._vehiculos.listar(limit=_LIMITE)
            conductores = await self._conductores.listar(limit=_LIMITE)
            nombres = {c.id: c.nombre for c in conductores}
            reporte = ReporteVehiculos(formato, vehiculos, nombres)
        elif tipo == "conductores":
            reporte = ReporteConductores(formato, await self._conductores.listar(limit=_LIMITE))
        elif tipo == "resumen":
            reporte = ReporteResumenFlota(formato, await self._vehiculos.listar(limit=_LIMITE))
        else:
            raise ReporteNoSoportado(f"No existe el reporte '{tipo}'")
        return reporte.generar()
