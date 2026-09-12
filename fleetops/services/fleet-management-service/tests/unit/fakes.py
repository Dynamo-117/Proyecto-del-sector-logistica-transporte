from __future__ import annotations

from typing import Any
from uuid import UUID

from app.domain.entities import Conductor, Usuario, Vehiculo
from app.infrastructure.db.repositorio_factory import RepositorioFactory


class FakeVehiculoRepository:
    def __init__(self):
        self._vehiculos: dict[UUID, Vehiculo] = {}

    async def crear(self, vehiculo: Vehiculo) -> Vehiculo:
        self._vehiculos[vehiculo.id] = vehiculo
        return vehiculo

    async def obtener_por_id(self, vehiculo_id: UUID) -> Vehiculo | None:
        return self._vehiculos.get(vehiculo_id)

    async def obtener_por_id_bloqueado(self, vehiculo_id: UUID) -> Vehiculo | None:
        return self._vehiculos.get(vehiculo_id)

    async def obtener_por_placa(self, placa: str) -> Vehiculo | None:
        return next((v for v in self._vehiculos.values() if v.placa == placa), None)

    async def listar(self, skip: int = 0, limit: int = 100) -> list[Vehiculo]:
        return list(self._vehiculos.values())[skip : skip + limit]

    async def actualizar(self, vehiculo: Vehiculo) -> Vehiculo:
        self._vehiculos[vehiculo.id] = vehiculo
        return vehiculo

    async def eliminar(self, vehiculo_id: UUID) -> None:
        self._vehiculos.pop(vehiculo_id, None)


class FakeConductorRepository:
    def __init__(self):
        self._conductores: dict[UUID, Conductor] = {}

    async def crear(self, conductor: Conductor) -> Conductor:
        self._conductores[conductor.id] = conductor
        return conductor

    async def obtener_por_id(self, conductor_id: UUID) -> Conductor | None:
        return self._conductores.get(conductor_id)

    async def obtener_por_id_bloqueado(self, conductor_id: UUID) -> Conductor | None:
        return self._conductores.get(conductor_id)

    async def obtener_por_licencia(self, licencia: str) -> Conductor | None:
        return next((c for c in self._conductores.values() if c.licencia == licencia), None)

    async def listar(self, skip: int = 0, limit: int = 100) -> list[Conductor]:
        return list(self._conductores.values())[skip : skip + limit]

    async def actualizar(self, conductor: Conductor) -> Conductor:
        self._conductores[conductor.id] = conductor
        return conductor

    async def eliminar(self, conductor_id: UUID) -> None:
        self._conductores.pop(conductor_id, None)


class FakeUsuarioRepository:
    def __init__(self):
        self._usuarios: dict[UUID, Usuario] = {}

    async def crear(self, usuario: Usuario) -> Usuario:
        self._usuarios[usuario.id] = usuario
        return usuario

    async def obtener_por_id(self, usuario_id: UUID) -> Usuario | None:
        return self._usuarios.get(usuario_id)

    async def obtener_por_email(self, email: str) -> Usuario | None:
        return next((u for u in self._usuarios.values() if u.email == email), None)


class FakeEventPublisher:
    def __init__(self):
        self.eventos: list[tuple[str, dict[str, Any]]] = []

    async def publicar(self, routing_key: str, payload: dict[str, Any]) -> None:
        self.eventos.append((routing_key, payload))


class FakeRepositorioFactory(RepositorioFactory):
    """PATRON GOF: ABSTRACT FACTORY -- Fabrica concreta #2: la misma familia
    de repositorios (Vehiculo + Conductor + Usuario), respaldada en memoria
    en vez de PostgreSQL. `session` no se usa (los fakes no hablan con
    ninguna base de datos); se acepta solo para cumplir la misma interfaz
    que SqlAlchemyRepositorioFactory.

    Guarda una unica instancia de cada repositorio (no una nueva por
    llamada), para que dos pedidos del mismo repositorio dentro de un test
    compartan el mismo estado -- igual que una sesion real compartida
    dentro de una peticion."""

    def __init__(self):
        self._vehiculos = FakeVehiculoRepository()
        self._conductores = FakeConductorRepository()
        self._usuarios = FakeUsuarioRepository()

    def crear_vehiculo_repo(self, session: object = None) -> FakeVehiculoRepository:
        return self._vehiculos

    def crear_conductor_repo(self, session: object = None) -> FakeConductorRepository:
        return self._conductores

    def crear_usuario_repo(self, session: object = None) -> FakeUsuarioRepository:
        return self._usuarios
