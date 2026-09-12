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


class LecturaOdometroModel(Base):
    __tablename__ = "lecturas_odometro"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)
    kilometraje_km: Mapped[float] = mapped_column(Float, nullable=False)
    horas_motor: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EstadoMantenimientoModel(Base):
    __tablename__ = "estados_mantenimiento"

    vehiculo_id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(30), primary_key=True)
    km_base: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    horas_base: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class AlertaModel(Base):
    __tablename__ = "alertas"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    kilometraje_km: Mapped[float] = mapped_column(Float, nullable=False)
    horas_motor: Mapped[float] = mapped_column(Float, nullable=False)
    generada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    resuelta_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
