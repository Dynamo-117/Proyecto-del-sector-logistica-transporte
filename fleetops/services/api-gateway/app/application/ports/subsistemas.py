from __future__ import annotations

from typing import Any, Protocol


class FlotaApi(Protocol):
    async def listar_vehiculos(self, headers: dict[str, str]) -> list[dict[str, Any]]: ...

    async def listar_conductores(self, headers: dict[str, str]) -> list[dict[str, Any]]: ...


class RutasApi(Protocol):
    async def listar_rutas_activas(self, headers: dict[str, str]) -> list[dict[str, Any]]: ...


class MantenimientoApi(Protocol):
    async def contar_alertas_activas(self, vehiculo_id: str, headers: dict[str, str]) -> int:
        """Alertas ACTIVAS del vehiculo; 0 si el servicio no lo conoce."""
        ...


class TrackingApi(Protocol):
    async def estado_movimiento(self, vehiculo_id: str, headers: dict[str, str]) -> str | None:
        """EN_MOVIMIENTO / DETENIDO, o None si el vehiculo no tiene telemetria."""
        ...
