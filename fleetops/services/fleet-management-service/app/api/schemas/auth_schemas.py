from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import RolUsuario


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    rol: RolUsuario
    activo: bool
