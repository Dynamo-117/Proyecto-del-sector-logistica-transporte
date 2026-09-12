from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import EstadoRuta, Ruta
from app.infrastructure.db.models import RutaModel
from app.infrastructure.db.repositorio_creador import RepositorioCreador


def _to_entity(model: RutaModel) -> Ruta:
    return Ruta(
        id=model.id,
        carga_id=model.carga_id,
        vehiculo_id=model.vehiculo_id,
        nodos=[UUID(n) for n in model.nodos],
        distancia_km=model.distancia_km,
        estado=EstadoRuta(model.estado),
        creado_en=model.creado_en,
    )


class SqlAlchemyRutaRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def crear(self, ruta: Ruta) -> Ruta:
        model = RutaModel(
            id=ruta.id,
            carga_id=ruta.carga_id,
            vehiculo_id=ruta.vehiculo_id,
            nodos=[str(n) for n in ruta.nodos],
            distancia_km=ruta.distancia_km,
            estado=ruta.estado.value,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def obtener(self, ruta_id: UUID) -> Ruta | None:
        model = await self._session.get(RutaModel, ruta_id)
        return _to_entity(model) if model else None

    async def listar_por_estado(self, estado: EstadoRuta) -> list[Ruta]:
        stmt = (
            select(RutaModel).where(RutaModel.estado == estado.value).order_by(RutaModel.creado_en)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]

    async def existe_ruta_activa_para_vehiculo(self, vehiculo_id: UUID) -> bool:
        stmt = select(RutaModel.id).where(
            RutaModel.vehiculo_id == vehiculo_id, RutaModel.estado == EstadoRuta.ACTIVA.value
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None


class RutaRepositorioCreador(RepositorioCreador[SqlAlchemyRutaRepository]):
    """PATRON GOF: FACTORY METHOD -- Creadora concreta de SqlAlchemyRutaRepository."""

    def crear_repositorio(self, session: AsyncSession) -> SqlAlchemyRutaRepository:
        return SqlAlchemyRutaRepository(session)
