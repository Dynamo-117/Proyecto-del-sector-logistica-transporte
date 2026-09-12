from __future__ import annotations

import threading
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "vehicle-tracking-service"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://fleetops:fleetops@localhost:5432/vehicle_tracking"

    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "fleetops.events"
    rabbitmq_queue: str = "vehicle-tracking.vehiculo-creado"
    rabbitmq_routing_key: str = "vehiculo.creado"

    cors_origins: list[str] = ["*"]

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
