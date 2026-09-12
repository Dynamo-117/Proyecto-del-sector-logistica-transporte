from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import LecturaOdometro
from app.infrastructure.db.models import LecturaOdometroModel


def _to_entity(model: LecturaOdometroModel) -> LecturaOdometro:
    return LecturaOdometro(
        id=model.id,
        vehiculo_id=model.vehiculo_id,
        kilometraje_km=model.kilometraje_km,
        horas_motor=model.horas_motor,
        timestamp=model.timestamp,
    )


class SqlAlchemyLecturaOdometroRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def guardar(self, lectura: LecturaOdometro) -> LecturaOdometro:
        model = LecturaOdometroModel(
            id=lectura.id,
            vehiculo_id=lectura.vehiculo_id,
            kilometraje_km=lectura.kilometraje_km,
            horas_motor=lectura.horas_motor,
            timestamp=lectura.timestamp,
        )
        self._session.add(model)
        await self._session.commit()
        return lectura

    async def obtener_mas_reciente(self, vehiculo_id: UUID) -> LecturaOdometro | None:
        stmt = (
            select(LecturaOdometroModel)
            .where(LecturaOdometroModel.vehiculo_id == vehiculo_id)
            .order_by(LecturaOdometroModel.timestamp.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None
