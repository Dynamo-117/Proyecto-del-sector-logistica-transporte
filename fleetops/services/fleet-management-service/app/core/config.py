from __future__ import annotations

import threading
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "fleet-management-service"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://fleetops:fleetops@localhost:5432/fleet_management"

    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "fleetops.events"

    jwt_secret_key: str = "dev-secret-cambiar-en-produccion"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutos: int = 60

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
    # ============================================================
    _instancia: ClassVar[Settings | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @classmethod
    def obtener_instancia(cls) -> Settings:

        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    cls._instancia = cls()
        return cls._instancia

    # ================= PATRON GOF: SINGLETON -- termina aqui =================


def get_settings() -> Settings:
    return Settings.obtener_instancia()
