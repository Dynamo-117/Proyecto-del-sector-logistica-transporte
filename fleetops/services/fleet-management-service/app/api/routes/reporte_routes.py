from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response

from app.api.dependencies import ConductorRepo, VehiculoRepo
from app.application.use_cases.reporte_use_cases import GenerarReporte
from app.infrastructure.reportes.formatos import FORMATOS

router = APIRouter(prefix="/reportes", tags=["reportes"])


def get_generar_reporte(
    vehiculo_repo: VehiculoRepo, conductor_repo: ConductorRepo
) -> GenerarReporte:
    return GenerarReporte(vehiculo_repo, conductor_repo)


@router.get(
    "/{tipo}",
    summary="Generar un reporte en el formato indicado",
    description=(
        "Tipos: vehiculos, conductores, resumen. Formatos: csv, json, html. "
        "Cualquier tipo puede escribirse en cualquier formato (patron Bridge)."
    ),
)
async def generar_reporte(
    tipo: str,
    use_case: Annotated[GenerarReporte, Depends(get_generar_reporte)],
    formato: Annotated[Literal["csv", "json", "html"], Query()] = "csv",
    descargar: Annotated[bool, Query()] = True,
) -> Response:
    reporte = await use_case.ejecutar(tipo, FORMATOS[formato])
    cabeceras = {}
    if descargar:
        cabeceras["Content-Disposition"] = f'attachment; filename="{reporte.nombre_archivo}"'
    return Response(content=reporte.contenido, media_type=reporte.media_type, headers=cabeceras)
