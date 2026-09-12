from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import VehiculoConocido
from app.infrastructure.db.models import VehiculoConocidoModel


def _to_entity(model: VehiculoConocidoModel) -> VehiculoConocido:
    return VehiculoConocido(id=model.id, placa=model.placa, registrado_en=model.registrado_en)


class SqlAlchemyVehiculoConocidoRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def existe(self, vehiculo_id: UUID) -> bool:
        model = await self._session.get(VehiculoConocidoModel, vehiculo_id)
        return model is not None

    async def obtener(self, vehiculo_id: UUID) -> VehiculoConocido | None:
        model = await self._session.get(VehiculoConocidoModel, vehiculo_id)
        return _to_entity(model) if model else None

    async def registrar(self, vehiculo: VehiculoConocido) -> VehiculoConocido:
        model = VehiculoConocidoModel(id=vehiculo.id, placa=vehiculo.placa)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)
