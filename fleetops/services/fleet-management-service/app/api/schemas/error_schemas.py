from pydantic import BaseModel


class ErrorResponse(BaseModel):
    codigo: str
    mensaje: str
    detalle: str | None = None
