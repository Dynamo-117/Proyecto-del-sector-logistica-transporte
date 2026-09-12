from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import EstadoVehiculo, TipoVehiculo, Vehiculo
from app.infrastructure.db.models import VehiculoModel


def _to_entity(model: VehiculoModel) -> Vehiculo:
    return Vehiculo(
        id=model.id,
        placa=model.placa,
        tipo=TipoVehiculo(model.tipo),
        capacidad_kg=model.capacidad_kg,
        estado=EstadoVehiculo(model.estado),
        conductor_id=model.conductor_id,
        creado_en=model.creado_en,
        actualizado_en=model.actualizado_en,
    )


class SqlAlchemyVehiculoRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def crear(self, vehiculo: Vehiculo) -> Vehiculo:
        model = VehiculoModel(
            id=vehiculo.id,
            placa=vehiculo.placa,
            tipo=vehiculo.tipo.value,
            capacidad_kg=vehiculo.capacidad_kg,
            estado=vehiculo.estado.value,
            conductor_id=vehiculo.conductor_id,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def obtener_por_id(self, vehiculo_id: UUID) -> Vehiculo | None:
        model = await self._session.get(VehiculoModel, vehiculo_id)
        return _to_entity(model) if model else None

    async def obtener_por_id_bloqueado(self, vehiculo_id: UUID) -> Vehiculo | None:
        # SQLite (usado en tests de integracion) no soporta FOR UPDATE.
        stmt = select(VehiculoModel).where(VehiculoModel.id == vehiculo_id)
        if self._session.bind.dialect.name != "sqlite":
            stmt = stmt.with_for_update()
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def obtener_por_placa(self, placa: str) -> Vehiculo | None:
        stmt = select(VehiculoModel).where(VehiculoModel.placa == placa)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def listar(self, skip: int = 0, limit: int = 100) -> list[Vehiculo]:
        stmt = select(VehiculoModel).offset(skip).limit(limit).order_by(VehiculoModel.creado_en)
        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]

    async def actualizar(self, vehiculo: Vehiculo) -> Vehiculo:
        model = await self._session.get(VehiculoModel, vehiculo.id)
        if model is None:
            raise ValueError(f"Vehiculo '{vehiculo.id}' no existe")

        model.tipo = vehiculo.tipo.value
        model.capacidad_kg = vehiculo.capacidad_kg
        model.estado = vehiculo.estado.value
        model.conductor_id = vehiculo.conductor_id

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def eliminar(self, vehiculo_id: UUID) -> None:
        model = await self._session.get(VehiculoModel, vehiculo_id)
        if model is not None:
            await self._session.delete(model)
            await self._session.commit()
