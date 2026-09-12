from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import EstadoVehiculo, VehiculoDisponible
from app.infrastructure.db.models import VehiculoDisponibleModel
from app.infrastructure.db.repositorio_creador import RepositorioCreador


def _to_entity(model: VehiculoDisponibleModel) -> VehiculoDisponible:
    return VehiculoDisponible(
        id=model.id,
        placa=model.placa,
        capacidad_kg=model.capacidad_kg,
        estado=EstadoVehiculo(model.estado),
    )


class SqlAlchemyVehiculoDisponibleRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def registrar_o_actualizar(self, vehiculo: VehiculoDisponible) -> VehiculoDisponible:
        model = await self._session.get(VehiculoDisponibleModel, vehiculo.id)
        if model is None:
            model = VehiculoDisponibleModel(
                id=vehiculo.id, placa=vehiculo.placa, capacidad_kg=0, estado=""
            )
            self._session.add(model)

        model.placa = vehiculo.placa
        model.capacidad_kg = vehiculo.capacidad_kg
        model.estado = vehiculo.estado.value

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def actualizar_estado(self, vehiculo_id: UUID, estado: EstadoVehiculo) -> None:
        model = await self._session.get(VehiculoDisponibleModel, vehiculo_id)
        if model is None:
            return
        model.estado = estado.value
        await self._session.commit()

    async def obtener(self, vehiculo_id: UUID) -> VehiculoDisponible | None:
        model = await self._session.get(VehiculoDisponibleModel, vehiculo_id)
        return _to_entity(model) if model else None

    async def listar_candidatos_bloqueado(self, peso_kg: float) -> list[VehiculoDisponible]:
        stmt = select(VehiculoDisponibleModel).where(
            VehiculoDisponibleModel.estado == EstadoVehiculo.DISPONIBLE.value,
            VehiculoDisponibleModel.capacidad_kg >= peso_kg,
        )
        # SQLite (usado en tests de integracion) no soporta FOR UPDATE.
        if self._session.bind.dialect.name != "sqlite":
            stmt = stmt.with_for_update()
        stmt = stmt.order_by(VehiculoDisponibleModel.capacidad_kg.asc())

        result = await self._session.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]


class VehiculoDisponibleRepositorioCreador(
    RepositorioCreador[SqlAlchemyVehiculoDisponibleRepository]
):
    """PATRON GOF: FACTORY METHOD -- Creadora concreta de
    SqlAlchemyVehiculoDisponibleRepository."""

    def crear_repositorio(self, session: AsyncSession) -> SqlAlchemyVehiculoDisponibleRepository:
        return SqlAlchemyVehiculoDisponibleRepository(session)
