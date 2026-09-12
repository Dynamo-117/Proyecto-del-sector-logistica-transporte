from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import VehiculoConocido
from app.infrastructure.db.models import VehiculoConocidoModel


class SqlAlchemyVehiculoConocidoRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def existe(self, vehiculo_id: UUID) -> bool:
        model = await self._session.get(VehiculoConocidoModel, vehiculo_id)
        return model is not None

    async def registrar_o_actualizar(self, vehiculo: VehiculoConocido) -> VehiculoConocido:
        model = await self._session.get(VehiculoConocidoModel, vehiculo.id)
        if model is None:
            model = VehiculoConocidoModel(id=vehiculo.id, placa=vehiculo.placa)
            self._session.add(model)
        else:
            model.placa = vehiculo.placa

        await self._session.commit()
        return vehiculo
