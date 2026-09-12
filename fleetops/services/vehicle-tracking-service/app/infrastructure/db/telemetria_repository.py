from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Telemetria
from app.infrastructure.db.models import TelemetriaModel


def _to_entity(model: TelemetriaModel) -> Telemetria:
    return Telemetria(
        id=model.id,
        vehiculo_id=model.vehiculo_id,
        latitud=model.latitud,
        longitud=model.longitud,
        velocidad_kmh=model.velocidad_kmh,
        timestamp=model.timestamp,
    )


class SqlAlchemyTelemetriaRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def guardar(self, telemetria: Telemetria) -> Telemetria:
        model = TelemetriaModel(
            id=telemetria.id,
            vehiculo_id=telemetria.vehiculo_id,
            latitud=telemetria.latitud,
            longitud=telemetria.longitud,
            velocidad_kmh=telemetria.velocidad_kmh,
            timestamp=telemetria.timestamp,
        )
        self._session.add(model)
        await self._session.commit()
        return telemetria

    async def obtener_mas_reciente(self, vehiculo_id: UUID) -> Telemetria | None:
        stmt = (
            select(TelemetriaModel)
            .where(TelemetriaModel.vehiculo_id == vehiculo_id)
            .order_by(TelemetriaModel.timestamp.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar_historico(
        self,
        vehiculo_id: UUID,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Telemetria]:
        stmt = select(TelemetriaModel).where(TelemetriaModel.vehiculo_id == vehiculo_id)
        if desde is not None:
            stmt = stmt.where(TelemetriaModel.timestamp >= desde)
        if hasta is not None:
            stmt = stmt.where(TelemetriaModel.timestamp <= hasta)
        stmt = stmt.order_by(TelemetriaModel.timestamp.desc()).offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]
