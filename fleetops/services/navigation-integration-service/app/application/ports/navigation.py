from __future__ import annotations

from typing import Protocol

from app.domain.entities import Coordenada, Ruta


class NavigationProvider(Protocol):
    async def calcular_ruta(self, origen: Coordenada, destino: Coordenada) -> Ruta: ...
