from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class RepositorioCreador(ABC, Generic[T]):
    # =================   PATRON GOF: FACTORY METHOD -- inicia aqui =================
  
    @abstractmethod
    def crear_repositorio(self, session: AsyncSession) -> T:
    #El metodo fabrica. Cada Creadora concreta decide aqui que
    #clase de repositorio instanciar.
        ...

    def obtener_repositorio(self, session: AsyncSession) -> T:
    #Punto de acceso que usa el metodo fabrica. No sabe (ni le
    #importa) que clase concreta de repositorio va a recibir."""
        return self.crear_repositorio(session)

    # ================= PATRON GOF: FACTORY METHOD -- termina aqui =================
