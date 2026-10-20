from __future__ import annotations

from abc import ABC, abstractmethod


class FormatoReporte(ABC):
    # =================   PATRON GOF: BRIDGE (Implementador) -- inicia aqui =================
    """El Implementador: la interfaz de la jerarquia "como se escribe un
    reporte". Solo conoce operaciones primitivas (titulo, columnas y filas ya
    convertidas a texto) y no sabe de que reporte se trata (vehiculos,
    conductores, ...). Cada formato concreto (CSV, JSON, HTML) la implementa a su
    manera; agregar uno nuevo no obliga a tocar ningun reporte.
    """

    media_type: str
    extension: str

    @abstractmethod
    def render(self, titulo: str, columnas: list[str], filas: list[list[str]]) -> str: ...

    # ================= PATRON GOF: BRIDGE (Implementador) -- termina aqui =================
