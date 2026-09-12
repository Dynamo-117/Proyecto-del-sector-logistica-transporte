from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_autenticar_usuario, get_obtener_usuario_autenticado
from app.api.schemas.auth_schemas import LoginRequest, TokenResponse, UsuarioResponse
from app.application.use_cases.auth_use_cases import AutenticarUsuario, ObtenerUsuarioAutenticado
from app.domain.exceptions import TokenInvalido

router = APIRouter(prefix="/auth", tags=["auth"])


def _extraer_token(request: Request) -> str:
    header = request.headers.get("authorization", "")
    if not header.lower().startswith("bearer "):
        raise TokenInvalido("Falta el header Authorization Bearer")
    return header[len("Bearer ") :]


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesion",
    description="Valida email/password y devuelve un JWT con el id y rol del usuario.",
)
async def login(
    payload: LoginRequest,
    use_case: Annotated[AutenticarUsuario, Depends(get_autenticar_usuario)],
) -> TokenResponse:
    token = await use_case.ejecutar(payload.email, payload.password)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Usuario autenticado actual",
    description="Devuelve el usuario correspondiente al JWT enviado en el header Authorization.",
)
async def me(
    request: Request,
    use_case: Annotated[ObtenerUsuarioAutenticado, Depends(get_obtener_usuario_autenticado)],
) -> UsuarioResponse:
    token = _extraer_token(request)
    usuario = await use_case.ejecutar(token)
    return UsuarioResponse.model_validate(usuario)
