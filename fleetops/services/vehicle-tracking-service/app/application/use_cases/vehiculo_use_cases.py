from __future__ import annotations

from uuid import UUID

from app.application.ports.repositories import VehiculoConocidoRepository
from app.domain.entities import VehiculoConocido


class RegistrarVehiculoConocido:
    """Registra un vehiculo del que este servicio tuvo noticia via evento
    'vehiculo.creado' de fleet-management-service. Idempotente: si el vehiculo
    ya estaba registrado (p.ej. por reentrega del mensaje), no hace nada."""

    def __init__(self, repo: VehiculoConocidoRepository):
        self._repo = repo

    async def ejecutar(self, vehiculo_id: UUID, placa: str) -> VehiculoConocido:
        existente = await self._repo.obtener(vehiculo_id)
        if existente is not None:
            return existente

        return await self._repo.registrar(VehiculoConocido(id=vehiculo_id, placa=placa))
