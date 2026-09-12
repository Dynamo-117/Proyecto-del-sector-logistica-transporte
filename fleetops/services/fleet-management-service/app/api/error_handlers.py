from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.domain.exceptions import DomainError

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        logger.warning(
            "domain_error", codigo=exc.codigo, mensaje=exc.mensaje, path=request.url.path
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"codigo": exc.codigo, "mensaje": exc.mensaje, "detalle": None},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "codigo": "VALIDACION_FALLIDA",
                "mensaje": "Los datos enviados no son validos",
                "detalle": str(exc.errors()),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("error_no_manejado", error=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "codigo": "ERROR_INTERNO",
                "mensaje": "Ocurrio un error interno inesperado",
                "detalle": None,
            },
        )
