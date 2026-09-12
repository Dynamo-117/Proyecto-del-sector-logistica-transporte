from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Arista
from app.infrastructure.db.models import AristaModel
from app.infrastructure.db.repositorio_creador import RepositorioCreador


def _to_entity(model: AristaModel) -> Arista:
    return Arista(
        id=model.id,
        nodo_origen_id=model.nodo_origen_id,
        nodo_destino_id=model.nodo_destino_id,
        distancia_km=model.distancia_km,
    )


class SqlAlchemyAristaRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def crear(self, arista: Arista) -> Arista:
        model = AristaModel(
            id=arista.id,
            nodo_origen_id=arista.nodo_origen_id,
            nodo_destino_id=arista.nodo_destino_id,
            distancia_km=arista.distancia_km,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def listar_todas(self) -> list[Arista]:
        result = await self._session.execute(select(AristaModel))
        return [_to_entity(m) for m in result.scalars().all()]


class AristaRepositorioCreador(RepositorioCreador[SqlAlchemyAristaRepository]):
    """PATRON GOF: FACTORY METHOD -- Creadora concreta de SqlAlchemyAristaRepository."""

    def crear_repositorio(self, session: AsyncSession) -> SqlAlchemyAristaRepository:
        return SqlAlchemyAristaRepository(session)
