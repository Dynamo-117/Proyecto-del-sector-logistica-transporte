from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import EstadoMantenimiento, TipoAlerta
from app.infrastructure.db.models import EstadoMantenimientoModel


class SqlAlchemyEstadoMantenimientoRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def obtener_todos(self, vehiculo_id: UUID) -> dict[TipoAlerta, EstadoMantenimiento]:
        stmt = select(EstadoMantenimientoModel).where(
            EstadoMantenimientoModel.vehiculo_id == vehiculo_id
        )
        result = await self._session.execute(stmt)
        return {
            TipoAlerta(m.tipo): EstadoMantenimiento(
                vehiculo_id=m.vehiculo_id,
                tipo=TipoAlerta(m.tipo),
                km_base=m.km_base,
                horas_base=m.horas_base,
            )
            for m in result.scalars().all()
        }

    async def actualizar_base(
        self, vehiculo_id: UUID, tipo: TipoAlerta, km_base: float, horas_base: float
    ) -> None:
        model = await self._session.get(EstadoMantenimientoModel, (vehiculo_id, tipo.value))
        if model is None:
            model = EstadoMantenimientoModel(vehiculo_id=vehiculo_id, tipo=tipo.value)
            self._session.add(model)

        model.km_base = km_base
        model.horas_base = horas_base
        await self._session.commit()
