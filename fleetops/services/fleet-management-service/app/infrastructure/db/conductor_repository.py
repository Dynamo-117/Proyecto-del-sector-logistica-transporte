from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Conductor, EstadoConductor
from app.infrastructure.db.models import ConductorModel


def _to_entity(model: ConductorModel) -> Conductor:
    return Conductor(
        id=model.id,
        nombre=model.nombre,
        licencia=model.licencia,
        estado=EstadoConductor(model.estado),
        creado_en=model.creado_en,
        actualizado_en=model.actualizado_en,
    )


class SqlAlchemyConductorRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def crear(self, conductor: Conductor) -> Conductor:
        model = ConductorModel(
            id=conductor.id,
            nombre=conductor.nombre,
            licencia=conductor.licencia,
            estado=conductor.estado.value,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def obtener_por_id(self, conductor_id: UUID) -> Conductor | None:
        model = await self._session.get(ConductorModel, conductor_id)
        return _to_entity(model) if model else None

    async def obtener_por_id_bloqueado(self, conductor_id: UUID) -> Conductor | None:
        stmt = select(ConductorModel).where(ConductorModel.id == conductor_id)
        if self._session.bind.dialect.name != "sqlite":
            stmt = stmt.with_for_update()
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def obtener_por_licencia(self, licencia: str) -> Conductor | None:
        stmt = select(ConductorModel).where(ConductorModel.licencia == licencia)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, skip: int = 0, limit: int = 100) -> list[Conductor]:
        stmt = select(ConductorModel).offset(skip).limit(limit).order_by(ConductorModel.creado_en)
        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]

    async def actualizar(self, conductor: Conductor) -> Conductor:
        model = await self._session.get(ConductorModel, conductor.id)
        if model is None:
            raise ValueError(f"Conductor '{conductor.id}' no existe")

        model.nombre = conductor.nombre
        model.estado = conductor.estado.value

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def eliminar(self, conductor_id: UUID) -> None:
        model = await self._session.get(ConductorModel, conductor_id)
        if model is not None:
            await self._session.delete(model)
            await self._session.commit()
