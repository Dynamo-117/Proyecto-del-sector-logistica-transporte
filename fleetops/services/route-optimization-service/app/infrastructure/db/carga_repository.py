from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Carga, EstadoCarga
from app.infrastructure.db.models import CargaModel
from app.infrastructure.db.repositorio_creador import RepositorioCreador


def _to_entity(model: CargaModel) -> Carga:
    return Carga(
        id=model.id,
        origen_nodo_id=model.origen_nodo_id,
        destino_nodo_id=model.destino_nodo_id,
        peso_kg=model.peso_kg,
        volumen_m3=model.volumen_m3,
        estado=EstadoCarga(model.estado),
        creado_en=model.creado_en,
    )


class SqlAlchemyCargaRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def crear(self, carga: Carga) -> Carga:
        model = CargaModel(
            id=carga.id,
            origen_nodo_id=carga.origen_nodo_id,
            destino_nodo_id=carga.destino_nodo_id,
            peso_kg=carga.peso_kg,
            volumen_m3=carga.volumen_m3,
            estado=carga.estado.value,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def actualizar_estado(self, carga_id: UUID, estado: EstadoCarga) -> Carga:
        model = await self._session.get(CargaModel, carga_id)
        if model is None:
            raise ValueError(f"Carga '{carga_id}' no existe")
        model.estado = estado.value
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def obtener(self, carga_id: UUID) -> Carga | None:
        model = await self._session.get(CargaModel, carga_id)
        return _to_entity(model) if model else None


class CargaRepositorioCreador(RepositorioCreador[SqlAlchemyCargaRepository]):
    """PATRON GOF: FACTORY METHOD -- Creadora concreta de SqlAlchemyCargaRepository."""

    def crear_repositorio(self, session: AsyncSession) -> SqlAlchemyCargaRepository:
        return SqlAlchemyCargaRepository(session)
