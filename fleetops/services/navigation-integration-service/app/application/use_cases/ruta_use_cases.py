from __future__ import annotations

from app.application.ports.navigation import NavigationProvider
from app.domain.entities import Coordenada, Ruta


class CalcularRuta:
    """Punto unico y normalizado del servicio: delega en el proveedor externo
    de navegacion configurado (OSRM por defecto) sin exponer sus detalles."""

    def __init__(self, provider: NavigationProvider):
        self._provider = provider

    async def ejecutar(self, origen: Coordenada, destino: Coordenada) -> Ruta:
        return await self._provider.calcular_ruta(origen, destino)
