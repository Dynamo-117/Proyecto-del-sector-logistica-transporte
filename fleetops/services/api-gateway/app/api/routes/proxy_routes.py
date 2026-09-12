from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_reenviar_peticion
from app.api.header_utils import filtrar_headers_entrantes, filtrar_headers_salientes
from app.application.use_cases.proxy_use_cases import ReenviarPeticion
from app.core.logging import correlation_id_var

router = APIRouter(tags=["proxy"])

METODOS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


async def _reenviar(
    request: Request, prefijo: str, resto_path: str, use_case: ReenviarPeticion
) -> StreamingResponse:
    correlation_id = correlation_id_var.get() or ""
    headers = filtrar_headers_entrantes(request.headers, correlation_id)
    content = await request.body()

    respuesta_backend = await use_case.ejecutar(
        prefijo, resto_path, request.method, headers, dict(request.query_params), content
    )

    async def cuerpo():
        try:
            async for chunk in respuesta_backend.aiter_raw():
                yield chunk
        finally:
            await respuesta_backend.aclose()

    return StreamingResponse(
        cuerpo(),
        status_code=respuesta_backend.status_code,
        headers=filtrar_headers_salientes(respuesta_backend.headers),
    )


@router.api_route("/{prefijo}", methods=METODOS)
async def proxy_raiz(
    request: Request,
    prefijo: str,
    use_case: Annotated[ReenviarPeticion, Depends(get_reenviar_peticion)],
) -> StreamingResponse:
    return await _reenviar(request, prefijo, "", use_case)


@router.api_route("/{prefijo}/{resto_path:path}", methods=METODOS)
async def proxy_con_path(
    request: Request,
    prefijo: str,
    resto_path: str,
    use_case: Annotated[ReenviarPeticion, Depends(get_reenviar_peticion)],
) -> StreamingResponse:
    return await _reenviar(request, prefijo, resto_path, use_case)
