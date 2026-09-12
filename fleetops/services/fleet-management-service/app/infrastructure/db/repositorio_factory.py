from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories import (
    ConductorRepository,
    UsuarioRepository,
    VehiculoRepository,
)
from app.infrastructure.db.conductor_repository import SqlAlchemyConductorRepository
from app.infrastructure.db.usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.db.vehiculo_repository import SqlAlchemyVehiculoRepository


class RepositorioFactory(ABC):
    
    #================= PATRON GOF: ABSTRACT FACTORY -- inicia aqui =    ================


    @abstractmethod
    def crear_vehiculo_repo(self, session: AsyncSession) -> VehiculoRepository: ...

    @abstractmethod
    def crear_conductor_repo(self, session: AsyncSession) -> ConductorRepository: ...

    @abstractmethod
    def crear_usuario_repo(self, session: AsyncSession) -> UsuarioRepository: ...

    # ================= PATRON GOF: ABSTRACT FACTORY -- termina aqui =================


class SqlAlchemyRepositorioFactory(RepositorioFactory):
    #Fabrica concreta: familia de repositorios respaldada por PostgreSQL (o SQLite en pruebas de integracion) a traves de SQLAlchemy.

    def crear_vehiculo_repo(self, session: AsyncSession) -> VehiculoRepository:
        return SqlAlchemyVehiculoRepository(session)

    def crear_conductor_repo(self, session: AsyncSession) -> ConductorRepository:
        return SqlAlchemyConductorRepository(session)

    def crear_usuario_repo(self, session: AsyncSession) -> UsuarioRepository:
        return SqlAlchemyUsuarioRepository(session)
