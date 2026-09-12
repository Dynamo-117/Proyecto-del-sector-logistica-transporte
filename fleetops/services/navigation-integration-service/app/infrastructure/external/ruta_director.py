from __future__ import annotations

from typing import Any

from app.domain.entities import Coordenada, Ruta
from app.domain.ruta_builder import RutaBuilder


class RutaDirector:
    # =================   PATRON GOF: BUILDER -- inicia aqui =================
    

    def construir_desde_respuesta_osrm(
        self, origen: Coordenada, destino: Coordenada, ruta_osrm: dict[str, Any]
    ) -> Ruta:
        return (
            RutaBuilder()
            .con_extremos(origen, destino)
            .con_metricas(
                distancia_metros=ruta_osrm["distance"],
                duracion_segundos=ruta_osrm["duration"],
            )
            .con_geometria(ruta_osrm["geometry"]["coordinates"])
            .construir()
        )

    # ================= PATRON GOF: BUILDER -- termina aqui =================
