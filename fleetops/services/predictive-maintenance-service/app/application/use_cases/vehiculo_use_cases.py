from __future__ import annotations

from uuid import UUID

from app.application.ports.repositories import VehiculoConocidoRepository
from app.domain.entities import VehiculoConocido


class SincronizarVehiculoConocido:
    """Mantiene al dia el modelo de lectura local de vehiculos a partir de los
    eventos 'vehiculo.creado'/'vehiculo.actualizado' de fleet-management-service."""

    def __init__(self, repo: VehiculoConocidoRepository):
        self._repo = repo

    async def ejecutar(self, vehiculo_id: UUID, placa: str) -> VehiculoConocido:
        return await self._repo.registrar_o_actualizar(
            VehiculoConocido(id=vehiculo_id, placa=placa)
        )
