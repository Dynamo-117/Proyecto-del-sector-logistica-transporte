from __future__ import annotations

from uuid import UUID

from app.application.ports.repositories import ConductorRepository
from app.domain.entities import Conductor, EstadoConductor
from app.domain.exceptions import ConductorNoEncontrado, LicenciaDuplicada


class CrearConductor:
    def __init__(self, repo: ConductorRepository):
        self._repo = repo

    async def ejecutar(self, nombre: str, licencia: str) -> Conductor:
        existente = await self._repo.obtener_por_licencia(licencia)
        if existente is not None:
            raise LicenciaDuplicada(f"Ya existe un conductor con licencia '{licencia}'")

        conductor = Conductor(nombre=nombre, licencia=licencia)
        return await self._repo.crear(conductor)


class ObtenerConductor:
    def __init__(self, repo: ConductorRepository):
        self._repo = repo

    async def ejecutar(self, conductor_id: UUID) -> Conductor:
        conductor = await self._repo.obtener_por_id(conductor_id)
        if conductor is None:
            raise ConductorNoEncontrado(f"Conductor '{conductor_id}' no encontrado")
        return conductor


class ListarConductores:
    def __init__(self, repo: ConductorRepository):
        self._repo = repo

    async def ejecutar(self, skip: int = 0, limit: int = 100) -> list[Conductor]:
        return await self._repo.listar(skip=skip, limit=limit)


class ActualizarConductor:
    def __init__(self, repo: ConductorRepository):
        self._repo = repo

    async def ejecutar(
        self,
        conductor_id: UUID,
        nombre: str | None = None,
        estado: EstadoConductor | None = None,
    ) -> Conductor:
        conductor = await self._repo.obtener_por_id(conductor_id)
        if conductor is None:
            raise ConductorNoEncontrado(f"Conductor '{conductor_id}' no encontrado")

        if nombre is not None:
            conductor.nombre = nombre
        if estado is not None:
            conductor.estado = estado

        return await self._repo.actualizar(conductor)


class EliminarConductor:
    def __init__(self, repo: ConductorRepository):
        self._repo = repo

    async def ejecutar(self, conductor_id: UUID) -> None:
        conductor = await self._repo.obtener_por_id(conductor_id)
        if conductor is None:
            raise ConductorNoEncontrado(f"Conductor '{conductor_id}' no encontrado")
        await self._repo.eliminar(conductor_id)
