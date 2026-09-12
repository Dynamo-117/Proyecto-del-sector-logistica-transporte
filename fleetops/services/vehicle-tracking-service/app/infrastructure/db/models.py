import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.infrastructure.db.guid import GUID


class Base(DeclarativeBase):
    pass


class VehiculoConocidoModel(Base):
    __tablename__ = "vehiculos_conocidos"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True)
    placa: Mapped[str] = mapped_column(String(20), nullable=False)
    registrado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class TelemetriaModel(Base):
    """Historico de telemetria. En produccion esta tabla se convierte en
    hypertable de TimescaleDB particionada por 'timestamp' (ver migracion)."""

    __tablename__ = "telemetria"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, index=True)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)
    velocidad_kmh: Mapped[float] = mapped_column(Float, nullable=False)
