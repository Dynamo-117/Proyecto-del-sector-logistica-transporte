from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Nodo
from app.infrastructure.db.models import NodoModel
from app.infrastructure.db.repositorio_creador import RepositorioCreador


def _to_entity(model: NodoModel) -> Nodo:
    return Nodo(id=model.id, nombre=model.nombre, latitud=model.latitud, longitud=model.longitud)


class SqlAlchemyNodoRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def crear(self, nodo: Nodo) -> Nodo:
        model = NodoModel(
            id=nodo.id, nombre=nodo.nombre, latitud=nodo.latitud, longitud=nodo.longitud
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def obtener(self, nodo_id: UUID) -> Nodo | None:
        model = await self._session.get(NodoModel, nodo_id)
        return _to_entity(model) if model else None

    async def listar(self) -> list[Nodo]:
        result = await self._session.execute(select(NodoModel).order_by(NodoModel.nombre))
        return [_to_entity(m) for m in result.scalars().all()]


class NodoRepositorioCreador(RepositorioCreador[SqlAlchemyNodoRepository]):
    """PATRON GOF: FACTORY METHOD -- Creadora concreta de SqlAlchemyNodoRepository."""

    def crear_repositorio(self, session: AsyncSession) -> SqlAlchemyNodoRepository:
        return SqlAlchemyNodoRepository(session)
