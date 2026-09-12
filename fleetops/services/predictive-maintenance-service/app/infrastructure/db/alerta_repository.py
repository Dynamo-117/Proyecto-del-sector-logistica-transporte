from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Alerta, EstadoAlerta, TipoAlerta
from app.infrastructure.db.models import AlertaModel


def _to_entity(model: AlertaModel) -> Alerta:
    return Alerta(
        id=model.id,
        vehiculo_id=model.vehiculo_id,
        tipo=TipoAlerta(model.tipo),
        estado=EstadoAlerta(model.estado),
        kilometraje_km=model.kilometraje_km,
        horas_motor=model.horas_motor,
        generada_en=model.generada_en,
        resuelta_en=model.resuelta_en,
    )


class SqlAlchemyAlertaRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def crear(self, alerta: Alerta) -> Alerta:
        model = AlertaModel(
            id=alerta.id,
            vehiculo_id=alerta.vehiculo_id,
            tipo=alerta.tipo.value,
            estado=alerta.estado.value,
            kilometraje_km=alerta.kilometraje_km,
            horas_motor=alerta.horas_motor,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def obtener(self, alerta_id: UUID) -> Alerta | None:
        model = await self._session.get(AlertaModel, alerta_id)
        return _to_entity(model) if model else None

    async def existe_activa(self, vehiculo_id: UUID, tipo: TipoAlerta) -> bool:
        stmt = select(AlertaModel.id).where(
            AlertaModel.vehiculo_id == vehiculo_id,
            AlertaModel.tipo == tipo.value,
            AlertaModel.estado == EstadoAlerta.ACTIVA.value,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def listar_por_vehiculo(self, vehiculo_id: UUID, estado: EstadoAlerta) -> list[Alerta]:
        stmt = (
            select(AlertaModel)
            .where(AlertaModel.vehiculo_id == vehiculo_id, AlertaModel.estado == estado.value)
            .order_by(AlertaModel.generada_en)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]

    async def actualizar(self, alerta: Alerta) -> Alerta:
        model = await self._session.get(AlertaModel, alerta.id)
        if model is None:
            raise ValueError(f"Alerta '{alerta.id}' no existe")

        model.estado = alerta.estado.value
        model.resuelta_en = alerta.resuelta_en

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)
