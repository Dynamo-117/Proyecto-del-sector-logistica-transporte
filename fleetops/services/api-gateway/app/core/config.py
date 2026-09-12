from __future__ import annotations

import threading
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "api-gateway"
    log_level: str = "INFO"

    fleet_management_url: str = "http://localhost:8000"
    vehicle_tracking_url: str = "http://localhost:8002"
    route_optimization_url: str = "http://localhost:8003"
    predictive_maintenance_url: str = "http://localhost:8004"
    navigation_integration_url: str = "http://localhost:8005"

    proxy_timeout_segundos: float = 30.0

    jwt_secret_key: str = "dev-secret-cambiar-en-produccion"
    jwt_algorithm: str = "HS256"

    cors_origins: list[str] = ["*"]

    @property
    def rutas_servicios(self) -> dict[str, str]:
        return {
            "fleet": self.fleet_management_url.rstrip("/"),
            "tracking": self.vehicle_tracking_url.rstrip("/"),
            "routing": self.route_optimization_url.rstrip("/"),
            "maintenance": self.predictive_maintenance_url.rstrip("/"),
            "navigation": self.navigation_integration_url.rstrip("/"),
        }

    # ============================================================
    # PATRON GOF: SINGLETON -- inicia aqui
    # ------------------------------------------------------------
    # Intencion: garantizar una unica instancia de Settings por
    # proceso y ofrecer un punto de acceso global a ella.
    #
    # Participantes:
    #   - Settings (esta clase)  -> el Singleton
    #   - _instancia              -> campo estatico privado (unica instancia)
    #   - _lock                   -> candado para creacion segura entre hilos
    #   - obtener_instancia()     -> punto de acceso global estatico
    #
    # Diagrama de clases, antes/despues y como verificarlo:
    # docs/patrones/singleton.md
    # ============================================================
    _instancia: ClassVar[Settings | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def obtener_instancia(cls) -> Settings:
        """Punto de acceso global del Singleton: crea la instancia la
        primera vez que se pide y devuelve siempre esa misma instancia.

        El "constructor privado" del patron clasico no se puede imponer
        al 100% en Python (pydantic necesita poder invocar __init__
        internamente), asi que se respeta por convencion: todo el
        codigo debe pasar por obtener_instancia() / get_settings(),
        nunca instanciar Settings() directamente.
        """
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    cls._instancia = cls()
        return cls._instancia

    # ================= PATRON GOF: SINGLETON -- termina aqui =================


def get_settings() -> Settings:
    return Settings.obtener_instancia()
