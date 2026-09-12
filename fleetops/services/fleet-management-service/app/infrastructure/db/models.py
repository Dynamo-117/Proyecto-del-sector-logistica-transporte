import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.infrastructure.db.guid import GUID


class Base(DeclarativeBase):
    pass


class VehiculoModel(Base):
    __tablename__ = "vehiculos"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    placa: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    capacidad_kg: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    conductor_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("conductores.id"), nullable=True
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    conductor: Mapped["ConductorModel | None"] = relationship(back_populates="vehiculo")


class ConductorModel(Base):
    __tablename__ = "conductores"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    licencia: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    vehiculo: Mapped["VehiculoModel | None"] = relationship(
        back_populates="conductor", uselist=False
    )


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
