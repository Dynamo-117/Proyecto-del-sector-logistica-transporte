from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import RolUsuario, Usuario
from app.infrastructure.db.models import UsuarioModel


def _to_entity(model: UsuarioModel) -> Usuario:
    return Usuario(
        id=model.id,
        email=model.email,
        password_hash=model.password_hash,
        rol=RolUsuario(model.rol),
        activo=model.activo,
        creado_en=model.creado_en,
        actualizado_en=model.actualizado_en,
    )


class SqlAlchemyUsuarioRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def crear(self, usuario: Usuario) -> Usuario:
        model = UsuarioModel(
            id=usuario.id,
            email=usuario.email,
            password_hash=usuario.password_hash,
            rol=usuario.rol.value,
            activo=usuario.activo,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def obtener_por_id(self, usuario_id: UUID) -> Usuario | None:
        model = await self._session.get(UsuarioModel, usuario_id)
        return _to_entity(model) if model else None

    async def obtener_por_email(self, email: str) -> Usuario | None:
        stmt = select(UsuarioModel).where(UsuarioModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None
